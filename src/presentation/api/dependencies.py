from fastapi import Depends
from infra.db_manager import DBManager
from domain.repository.operator_repository import OperatorRepository
from application.services.operator_service import OperatorSearchService

def get_db_manager():
    return DBManager()

def get_operator_repository(db_manager=Depends(get_db_manager)):
    return OperatorRepository(Depends(db_manager.get_db()))

def get_operator_service(operator_repository=Depends(get_operator_repository)):
    return OperatorSearchService(operator_repository)