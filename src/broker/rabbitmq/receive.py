from aio_pika import connect, ExchangeType 
from aio_pika.abc import AbstractIncomingMessage
import asyncio 
from src.schemas.notifications import AddNotificationsToDb
from src.email.send_email import send_email_about_password_reset
from src.services.notifications import NotificationsService
from src.repositories.notifications import NotificationsRepository
import src.logger 
import logging 

logger = logging.getLogger(__name__)
notification_service: NotificationsService = NotificationsService(NotificationsRepository)


async def main() -> None: 
    connection = await connect("amqp://guest:guest@localhost/")
    async with connection: 
        channel = await connection.channel() 

        # Declare queue 
        queue = await channel.declare_queue("echo_queue", exclusive=True) 

        # Declare exchange 
        echonet_exchange = await channel.declare_exchange(
            "echonet_exchange", ExchangeType.DIRECT
        )

        binding_keys = ["email", "notification"]

        # Bind 
        for binding_key in binding_keys:
            await queue.bind(echonet_exchange, routing_key=binding_key) 

        # Consume 
        logger.info("RabbitMQ start consuming...")
        
        async with queue.iterator() as iterator: 
            message: AbstractIncomingMessage 
            async for message in iterator: 
                if message.routing_key == "email":             
                    to_, from_, pin_code, ip, device, browser = message.body.decode().split(":")
                    logger.info(f"Receive email({to_}) for password change with pin code({pin_code[:3]}***)...")
                    send_email_about_password_reset(to_, from_, pin_code, ip, device, browser)
                elif message.routing_key == "notification":
                    user_id, status, message_for_notification = message.body.decode().split(":")
                    logger.info(f"Receive Notification('{message_for_notification}') for User({user_id})")
                    await notification_service.add(
                        AddNotificationsToDb(user_id=user_id, status=status, message=message_for_notification)
                    )

        await asyncio.Future()


if __name__ == "__main__": 
    asyncio.run(main()) 
