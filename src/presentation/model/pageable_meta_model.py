from pydantic import BaseModel, ConfigDict
from pydantic.dataclasses import dataclass
from presentation.model.operator_request_params import OperatorRequestParams

class SortData(BaseModel):
    sorted: bool
    property: str
    dir: str

@dataclass(frozen=True)   
class PageableMetaData:
    page: int
    page_size: int
    last_page: int
    sort: SortData
    
    @classmethod
    def from_criteria(cls, criteria: 'OperatorRequestParams', last_page: int) -> 'PageableMetaData':
        return cls(
            page=criteria.page,
            page_size=criteria.page_size,
            last_page=last_page,
            sort=SortData(sorted=True, property=criteria.order_by, dir=criteria.order_direction)
        )


    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)