from typing import List, Optional, Tuple

from sqlalchemy import Date, String, asc, desc, or_, collate, literal, func

from src.application.dto.operator_model import OperatorModel
from src.domain.model.operator import Operator
from src.presentation.model.operator_request_params import \
    OperatorRequestParams


class OperatorRepository:
    def __init__(self, session):
        self.session = session

    @staticmethod
    def apply_search_filter(base_query, search_term: str):
        if not search_term:
            return base_query

        search_pattern = f"%{search_term}%"
        string_columns = [
            column
            for column in Operator.__table__.columns
            if column.name != "id" and isinstance(column.type, String)
        ]

        conditions = [func.lower(func.unaccent(column)).like(
                func.lower(func.unaccent(literal(search_pattern))))
            for column in string_columns
        ]   
        return base_query.filter(or_(*conditions)) if conditions else base_query

    @staticmethod
    def apply_ordering(query, field: Optional[str], direction: str = "asc"):
        if not field:
            return query

        if hasattr(Operator, field):
            column = getattr(Operator, field)
        else:
            column = Operator.__table__.columns.get(field)
            if column is None:
                return query

        order_func = desc if direction == "desc" else asc
        return query.order_by(order_func(collate(column, "pt_br_ci_ai")))

    @staticmethod
    def paginate(query, page: int, page_size: int):
        return query.offset((page - 1) * page_size).limit(page_size)

    def search_operators(
        self, params: OperatorRequestParams
    ) -> Tuple[List[OperatorModel], int]:
        query = self.session.query(Operator)
        filtered_query = self.apply_search_filter(query, params.search)

        total_items = filtered_query.count()
        total_pages = max(1, (total_items + params.page_size - 1) // params.page_size)

        ordered_query = self.apply_ordering(
            filtered_query, params.sort_field, params.sort_direction
        )
        paginated_query = self.paginate(ordered_query, params.page, params.page_size)

        operators = [
            OperatorModel.model_validate(operator, from_attributes=True)
            for operator in paginated_query.all()
        ]

        return operators, total_pages
