from pydantic.dataclasses import dataclass
from typing import Any, List

from presentation.model.operator_request_params import OperatorRequestParams
from presentation.model.pageable_meta_model import PageableMetaData

@dataclass(frozen=True)
class PageableResponse:
    data: List[Any]
    meta: PageableMetaData

    @classmethod
    def create(cls, data: List[Any], criteria: OperatorRequestParams, last_page: int) -> 'PageableResponse':
        meta = PageableMetaData.from_criteria(criteria, last_page)
        return cls(data=data, meta=meta)