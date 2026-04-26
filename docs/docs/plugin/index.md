# Plugins

Plugins extend clickdetect with custom logic that runs when events occur during detection. They can enrich alert data, send it to external systems, or trigger any side effect your workflow requires.

## How plugins work

At startup, clickdetect automatically discovers every `.py` file inside `detector/plugins/` and registers any class that extends `PluginBase`. Plugins declared in `runner.yml` are then initialised with their configuration.

When a rule fires, the engine emits an event and calls every registered hook in order. Each hook can return updated template data, which is merged and passed to subsequent hooks and finally to webhooks.

## Configuring plugins

Plugins are configured under the `plugins` key in `runner.yml`. The key is the plugin `id` and the value is a free-form configuration object passed directly to the plugin's `run` method.

```yaml
plugins:
    <plugin_id>:
        option1: value1
        option2: value2
```

Example with the built-in clickagentic plugin:

```yaml
plugins:
    clickagentic:
        provider: openai
        model: gpt-4o-mini
        token: sk-...
```

## Available events

| Event | When it fires | Handler signature |
|---|---|---|
| `on_rule_triggered` | After a rule condition is met | `(rule, detector, result, template_data)` |

A hook handler returning a `dict` with a `template_data` key will merge its contents into the running template context, making the data available to subsequent hooks and to webhook templates.

## Creating a plugin

1. Create a new file in `clickdetect/detector/plugins/`, for example `myplugin.py`.
2. Subclass `PluginBase` and set the class-level `id`, `name`, and `version`.
3. Implement `run(config)` to initialise state from the YAML configuration.
4. Optionally implement `register_hooks(registry)` to subscribe to events.

```python
from typing import Any
from .base import PluginBase
from ..hooks import HookRegistry, EventEnum
from ..manager import Manager

class MyPlugin(PluginBase):
    id = "myplugin"
    name = "My custom plugin"
    version = "v0.1.0"

    async def run(self, config: Any):
        self.api_url = config.get("api_url")

    async def register_hooks(self, registry: HookRegistry) -> None:
        registry.register(EventEnum.on_rule_triggered, self._on_rule_triggered)

    async def _on_rule_triggered(self, rule, detector, result, template_data) -> dict | None:
        # Enrich template_data or trigger side effects here
        return {
            "template_data": {
                **template_data,
                "myplugin": {"api_url": self.api_url},
            }
        }
```

Then enable it in `runner.yml`:

```yaml
plugins:
    myplugin:
        api_url: https://my-service.internal/ingest
```

## Built-in plugins

| Plugin ID | Description |
|---|---|
| [`clickagentic`](clickagentic.md) | Analyses triggered alerts with an LLM and enriches template data with the result |
