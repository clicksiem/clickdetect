from dataclasses import dataclass
from typing import Any, Dict


@dataclass()
class DataSourceQueryResult:
    len: int
    value: Any
    datasource: str

    def to_dict(self) -> Dict[str, Any]:
        return {"len": self.len, "value": self.value, "datasource": self.datasource}


class BaseDataSource:
    async def connect(self):
        raise NotImplementedError()

    async def query(self, data: str) -> DataSourceQueryResult | None:
        raise NotImplementedError()

    @classmethod
    def _name(cls) -> str:
        raise NotImplementedError()

    async def _parse(self, _obj: Any):
        raise NotImplementedError()

    def to_dict(self) -> Dict:
        raise NotImplementedError()
