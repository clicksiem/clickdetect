# Datasources

## Datasource directory

```sh
./detector/datasource/
```

## Datasource base

```python
# file: ./detector/datasource/base.py
class BaseDataSource:
```

## Creating a new datasource

```python
class MyDataSource(BaseDataSource):
    async def connect(self):
        pass  # open connection

    async def query(self, data: str) -> DataSourceQueryResult | None:
        # execute query and return DataSourceQueryResult(len, rows)
        pass

    @classmethod
    def _name(cls) -> str:
        return 'mydatasource'

    async def _parse(self, _obj: Any):
        # parse config from runner.yml
        self.host = _obj.get('host')

    def to_dict(self) -> Dict:
        return { 'host': self.host }
```

## Add the new datasource to __init__.py

```python
# ./detector/datasource/__init__.py

datasources: List[Type[BaseDataSource]] = [
    ...,
    MyDataSource
]
```
