# Webhooks

## Webhook directory

```sh
./detector/webhooks/
```

## Webhook base

```python
# file: ./detector/webhooks/base.py
class BaseWebhook:
```

## Creating new webhook:

```python
class MyNewWebhook(BaseWebhook):
    async def send(self, data: str): # receive jinja2 template loaded from detector using self.template
        print(data)

    async def _parse(self, data: Any, template_data: Dict): # receive yaml loaded
        template_rendered = self.jinja_env.from_string(self.var_with_template).render(**template_data)
        self.name = data.get('name')
        self.type = MyNewWebhook._name()

    @classmethod
    def _name(cls) -> str:
        return 'mywebhook'

    def to_dict(self) -> Dict:
        return {
            self.name
        }

    def connect(self): # loaded on webhook creation
        pass

    def close(self): # loaded on webhook closing
        pass
```

## Add the new webhook to __init__.py


```python
# ./detector/webhooks/__init__.py

webhooks: List[Type[BaseWebhook]] = [
    ...,
    MyNewWebhook
]
```
