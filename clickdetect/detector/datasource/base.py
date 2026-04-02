from ..rules import Rule
from ..utils import Parameters
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass()
class DataSourceQueryResult:
    len: int
    value: Any
    datasource: str

    def to_dict(self) -> Dict[str, Any]:
        return {"len": self.len, "value": self.value, "datasource": self.datasource}


class BaseDataSource:
    params: List[Parameters] = []

    async def connect(self):
        raise NotImplementedError()

    async def _query(self, data: str, rule: Rule) -> DataSourceQueryResult | None:
        return await self.query(data)

    async def query(self, data: str) -> DataSourceQueryResult | None:
        raise NotImplementedError()

    @classmethod
    def _name(cls) -> str:
        raise NotImplementedError()

    @classmethod
    def _params(cls) -> List[Parameters]:
        raise NotImplementedError()

    async def _parse(self, data: Any):
        self.params = self._params()

        if missing := next(
            (p.name for p in self.params if p.required and p.name not in data), None
        ):
            raise ValueError(f"Required param not provided: {missing}")

        for param in self.params:
            value = data.get(param.name, param.default)
            if value is None:
                continue
            if param.type is not None:
                if param.type is list:
                    value = [value] if not isinstance(value, list) else value
                else:
                    value = param.type(value)
            setattr(self, param.attr_name or param.name, value)

    def to_dict(self) -> Dict:
        result: Dict[str, Any] = {"type": self._name()}
        for param in self._params():
            if param.is_sensive_field:  # not send fields like 'password'
                continue
            attr = param.attr_name or param.name
            result[param.name] = getattr(self, attr, param.default)
        return result

