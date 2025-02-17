from src.utils.repository import SQLAlchemyRepository 
from src.models.models import ReportedUser 


class ReportedUserRepository(SQLAlchemyRepository): 
    model = ReportedUser 
