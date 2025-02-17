from abc import abstractmethod, ABC 
from src.db.db import async_session_maker 
from sqlalchemy import select, insert, update, delete


class AbstractRepository(ABC): 
    @abstractmethod 
    async def get_all(self): 
        raise NotADirectoryError 
    
    @abstractmethod 
    async def get_by_filters(self, filters: dict, one=True): 
        raise NotImplementedError 
    
    @abstractmethod 
    async def update_one(self, entity_id: int, data: dict): 
        raise NotImplementedError 
    
    @abstractmethod 
    async def delete_one(self, entity_id: int): 
        raise NotImplementedError 
    
    @abstractmethod 
    async def add(self, data: dict): 
        raise NotImplementedError
    

class SQLAlchemyRepository(AbstractRepository): 
    model = None 

    async def get_all(self):
        async with async_session_maker() as session: 
            query = select(self.model)
            result = await session.execute(query) 
            return result.scalars().all()

    async def add(self, data: dict) -> int: 
        async with async_session_maker() as session: 
            query = insert(self.model).values(**data).returning(self.model.id)

            result = await session.execute(query)

            await session.commit() 

            return result.scalar()

    async def get_by_filters(self, filters: dict, one=True): 
        async with async_session_maker() as session: 
            query = select(self.model).filter_by(**filters) 
            result = await session.execute(query) 

            if one: 
                return result.scalar() 
            else: 
                return result.scalars().all() 
    
    async def update_one(self, entity_id: int, data: dict): 
        async with async_session_maker() as session: 
            query = update(self.model).where(self.model.id == entity_id).values(**data) 
            await session.execute(query) 
            await session.commit() 

    async def delete_one(self, entity_id: int): 
        async with async_session_maker() as session: 
            query = delete(self.model).where(self.model.id == entity_id)
            await session.execute(query) 
            await session.commit()
