from typing import List, Tuple
from sqlalchemy import String, or_, func
from domain.model.operator import Operator
from sqlalchemy.orm import Session
from application.dto.operator_model import OperatorModel
from presentation.model.operator_request_params import OperatorRequestParams

class OperatorRepository:
    def __init__(self, session: Session):
        self.session = session

    def search_operators(self, operator_params: OperatorRequestParams) -> Tuple[List[OperatorModel], int]:
        db_query = self.session.query(Operator)
        query = operator_params.query
        page = operator_params.page
        page_size = operator_params.page_size

        if query:
            search_pattern = f"%{query}%"

            conditions = []

            for column in Operator.__table__.columns:
                if column.name != 'id' and isinstance(column.type, String):
                    conditions.append(column.ilike(search_pattern))

            if conditions:
                db_query = db_query.filter(or_(*conditions))

        last_page = db_query.with_entities(func.ceil(func.count() / page_size)).scalar()
        paginated_query = db_query.offset((page - 1) * page_size).limit(page_size)
        operators = [
            OperatorModel.model_validate(operator)
            for operator in paginated_query.all()
        ]

        return operators, last_page