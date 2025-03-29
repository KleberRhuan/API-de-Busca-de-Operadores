from typing import List, Tuple
from sqlalchemy import String, or_, func, desc, asc
from src.domain.model.operator import Operator
from src.application.dto.operator_model import OperatorModel
from src.presentation.model.operator_request_params import OperatorRequestParams

class OperatorRepository:
    def __init__(self, session):
        self.session = session

    def search_operators(self, operator_params: OperatorRequestParams) -> Tuple[List[OperatorModel], int]:
        db_query = self.session.query(Operator)
        query = operator_params.query
        page = operator_params.page
        page_size = operator_params.page_size
        order_by = operator_params.order_by
        order_direction = operator_params.order_direction

        if query:
            search_pattern = f"%{query}%"
            conditions = []

            for column in Operator.__table__.columns:
                if column.name != 'id' and isinstance(column.type, String):
                    conditions.append(column.ilike(search_pattern))

            if conditions:
                db_query = db_query.filter(or_(*conditions))
        
        # Aplicar ordenação se especificado
        if order_by:
            column = getattr(Operator, order_by)
            if order_direction == 'desc':
                db_query = db_query.order_by(desc(column))
            else:
                db_query = db_query.order_by(asc(column))

        last_page = db_query.with_entities(func.ceil(func.count() / page_size)).scalar()
        paginated_query = db_query.offset((page - 1) * page_size).limit(page_size)
        operators = [
            OperatorModel.model_validate(operator, from_attributes=True)
            for operator in paginated_query.all()
        ]

        return operators, last_page