import re
from fastapi_utils.cbv import cbv 
from fastapi import APIRouter, HTTPException, status, Request, Response, Depends
from pydantic import EmailStr
from src.broker.send import send_message
from src.schemas.password_reset import PasswordResetAddToDb, PasswordResetPayload, PasswordResetResponse
from src.auth.dependencies import get_current_user
from src.schemas.ip_defender import IpDefenderAddToDbSchema, IpDefenderFiltersSchema
from src.schemas.users import UsersAddSchema, UsersAddToDbSchema, UsersAuthResponseSchema, UsersAuthSchema, UsersRegisterResponse, UsersUpdateSchema
from src.services.users import UsersService 
from src.services.password_reset import PasswordResetService
from src.services.ip_defender import IpDefenderService
from src.api.dependencies import users_service, ip_defender_service, password_reset_service
from src.auth.auth import authenticate_user, get_password_hash, create_access_token
from sqlalchemy.exc import SQLAlchemyError
from src.models.models import Users
from src.config import settings
from better_profanity import profanity
from datetime import datetime, timezone
from typing import Annotated
from string import digits
from random import SystemRandom
from user_agents import parse
import src.logger
import aiohttp
import asyncio
import logging 

router = APIRouter(prefix="/auth", tags=["Authentication & Registration"])


hashed_ips = {} # {ip: [status(True/False), applied_date_time]}
ips_reset_tries = {} # {ip: [attempts(max=2), applied_date_time]}


@cbv(router) 
class AuthApi: 
    def __init__(self): 
        self.users_service: UsersService = users_service()
        self.ip_defender_service: IpDefenderService = ip_defender_service()
        self.password_reset_service: PasswordResetService = password_reset_service()
        
        self.logger = logging.getLogger(__name__)

    @router.post("/registration", response_model=UsersRegisterResponse)
    async def registration(self, request: Request, data: UsersAddSchema) -> UsersRegisterResponse: 
        # Check email 
        if not (await self.check_email(data.email)): 
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid email. Please enter a valid email.")

        # Validate username 
        username = await self.validate_username(data.username)

        # Validate password 
        result = self.validate_password(data.password)
        if not result[0]:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=result[1])

        # Get hashed_password 
        hashed_password = get_password_hash(data.password)

         # Check IP for registartion permission 
        if not await self.ip_checker(request): 
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your IP is temporary block. You can return after 3 days.")

        try:
            user_id = await self.users_service.add(UsersAddToDbSchema(username=username, email=data.email, hashed_password=hashed_password))
            return UsersRegisterResponse(user_id=user_id)
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex)
            else: 
                self.logger.error("Unknown error: %s" % ex)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @router.post("/", response_model=UsersAuthResponseSchema)
    async def authentication(self, response: Response, data: UsersAuthSchema) -> UsersAuthResponseSchema:
        user = await authenticate_user(data.email, data.password, self.users_service)
        access_token = create_access_token({"sub": str(user.id)})
        response.set_cookie("access_token", access_token, httponly=True, max_age=settings.TOKEN_EXPIRE)
        return UsersAuthResponseSchema(AccessToken=access_token)
    
    @router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
    async def logout(self, response: Response, current_user: Annotated[Users, Depends(get_current_user)]): 
        response.delete_cookie("access_token") 
        return "", 204
    
    @router.post("/password/reset", status_code=status.HTTP_204_NO_CONTENT)
    async def reset_password(self, request: Request, current_user: Annotated[Users, Depends(get_current_user)]): 
        # Check password change availability
        password_reset_request = await self.password_reset_service.get_last_reset_request(current_user.id, un_used=False)
        if password_reset_request and password_reset_request.applied_date_time: 
            if datetime.now(timezone.utc).timestamp() - password_reset_request.applied_date_time.timestamp() < settings.PASS_RESET_MONTH: 
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can change password one time in a month")
        
        # Check local attempts
        ip = request.client.host
        if ip not in ips_reset_tries: 
            ips_reset_tries[ip] = [1, datetime.now(timezone.utc)] 
        else: 
            if ips_reset_tries[ip][0] == 2: 
                if datetime.now(timezone.utc).timestamp() - ips_reset_tries[ip][-1].timestamp() > settings.PASS_RESET_EXPIRE:
                    ips_reset_tries[ip] = [1, datetime.now(timezone.utc)]
                else:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Try again later") 
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Try again later") 

        # Get and check UserAgent
        user_agent = request.headers.get("user-agent", None)
        if user_agent is None: 
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        # Generate Pin Code 
        pin_code = self.generate_pin_code() 
        
        try: 
            await self.password_reset_service.add(PasswordResetAddToDb(user_id=current_user.id, pin_code=pin_code))
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex) 
            else: 
                self.logger.error("Unknown error: %s" % ex)
        
        # Parse UserAgent 
        parsed_ua = parse(user_agent) 

        # Info from request
        ip = request.client.host 
        browser = parsed_ua.browser.family 
        device = parsed_ua.device.family

        await send_message(f"{current_user.email}:{settings.SUPPORT_EMAIL}:{pin_code}:{ip}:{device}:{browser}", "email")
        ips_reset_tries[ip][0] += 1 

        return "", 204 

    @router.put("/password/reset/confirmation/{confirmation_code}", response_model=PasswordResetResponse)
    async def confirmation_password_reset(self, confirmation_code: int, data: PasswordResetPayload, current_user: Annotated[Users, Depends(get_current_user)]) -> PasswordResetResponse:
        # Get password reset request
        password_reset_request = None
        try: 
            password_reset_request = await self.password_reset_service.get_last_reset_request(current_user.id) 
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex) 
            else: 
                self.logger.error("Unknown error: %s" % ex)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) 

        # Check password reset request
        if password_reset_request is None: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no password reset request!")
        
        # Check password reset request expire
        if datetime.now(timezone.utc).timestamp() - password_reset_request.create_date_time.timestamp() > settings.PASS_RESET_EXPIRE: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request for password reset has been expired") 

        # Check pin_code 
        if password_reset_request.pin_code != confirmation_code: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong pin code for password reset")
        
        # Validate password 
        result = self.validate_password(data.password)
        if not result[0]:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=result[1])
        
        # Get hashed_password
        hashed_password = get_password_hash(data.password) 

        try:
            await self.users_service.update_one(current_user.id, UsersUpdateSchema(hashed_password=hashed_password))
            await self.password_reset_service.set_applied_date_time(current_user.id, datetime.now(timezone.utc))
            return PasswordResetResponse(user_id=current_user.id)
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex) 
            else: 
                self.logger.error("Unknown error: %s" % ex) 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def check_email(self, email: EmailStr):
        headers = {'x-rapidapi-host': settings.X_RAPIDAPI_HOST, 'x-rapidapi-key': settings.X_RAPIDAPI_KEY}
        params = {"email": email}

        for attempt in range(3):
            try:
                async with aiohttp.ClientSession() as session: 
                    async with session.get("https://email-checker.p.rapidapi.com/verify/v1", headers=headers, params=params) as response: 
                        result = await response.json()
                        return True if result["status"] == "valid" else False 
            except Exception as ex: 
                self.logger.error(f"Internal API error(attmept={attempt + 1}): %s" % ex)
                await asyncio.sleep(2) 

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error occurred during email validation.")

    async def validate_username(self, username: str) -> str: 
        return profanity.censor(username)
    
    async def ip_checker(self, request: Request) -> bool: 
        self.logger.info("Current TIME_BLOCK: %s" % settings.TIME_BLOCK)
        assert settings.TIME_BLOCK > 0, HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        client_ip = request.client.host

        if client_ip in hashed_ips:
            if datetime.now(timezone.utc).timestamp() - hashed_ips[client_ip][-1].timestamp() >= settings.TIME_BLOCK: 
                hashed_ips.pop(client_ip)
            else:
                return False

        ip = await self.ip_defender_service.get_by_filters(IpDefenderFiltersSchema(ip=client_ip))

        # Check that ip exists
        if ip is None: 
            await self.ip_defender_service.add(IpDefenderAddToDbSchema(ip=client_ip))
            await self.ip_defender_service.decrease_attempt(client_ip) 

            return True

        # Check attempt
        if ip.attempt - 1 >= 0: 
            await self.ip_defender_service.decrease_attempt(client_ip) 

            return True

        # Check TIME_BLOCK 
        if ip.applied_date_time: 
            if datetime.now(timezone.utc).timestamp() - ip.applied_date_time.timestamp() >= settings.TIME_BLOCK:
                await self.ip_defender_service.fill_attempt(client_ip)
                await self.ip_defender_service.decrease_attempt(client_ip)
                await self.ip_defender_service.set_applied_date_time(client_ip)

                return True
            else: 
                hashed_ips.update({client_ip: [False, datetime.now(timezone.utc)]})
                return False
        else:
            await self.ip_defender_service.set_applied_date_time(client_ip, datetime.now(timezone.utc))

            hashed_ips.update({client_ip: [False, datetime.now(timezone.utc)]})
            return False
    
    @staticmethod 
    def validate_password(password: str): 
        if len(password) < 6: 
            return False, "Password lenght must be greate or equal 6"
        
        if re.match(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).*$", password): 
            return True, ""
        
        return False, "Password must contain at least one uppercase letter, one lowercase letter and one digit."

    @staticmethod 
    def generate_pin_code() -> int: 
        cryptogen = SystemRandom()
        return int("".join([cryptogen.choice(digits) for _ in range(6)]))
