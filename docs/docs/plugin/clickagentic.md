# Clickagentic

Clickagentic is a built-in plugin that sends triggered alert data to an LLM for triage. For every rule that fires, the agent produces a structured analysis — summary, severity assessment, false-positive score, explanation, and concrete mitigation steps — and merges it into the template context so webhooks can include it in notifications.

## Configuration

```yaml
plugins:
    clickagentic:
        provider: <provider>        # required
        model: <model_name>         # required
        token: <api_key>            # required
        base_url: <url>             # optional – custom endpoint (Ollama, OpenRouter, etc.)
        false_positive: <text>      # optional – known false-positive context for the agent
        think: false                # optional – enable extended thinking (supported providers only)
```

## Install

You need to install clickagentic group

```
uv sync --group clickagentic
```

### Fields

| Field | Required | Description |
|---|---|---|
| `provider` | yes | LLM provider. See [Supported providers](#supported-providers) below. |
| `model` | yes | Model identifier as expected by the provider (e.g. `gpt-4o-mini`, `claude-sonnet-4-5`). |
| `token` | yes | API key for the provider. |
| `base_url` | no | Custom base URL. Required for Ollama; optional for OpenRouter. |
| `false_positive` | no | Free-text context describing known benign patterns. The agent uses this to calibrate the false-positive score. |
| `think` | no | Enables extended thinking mode. Default: `false`. |

## Supported providers

| Provider | `provider` value | Notes |
|---|---|---|
| OpenAI | `openai` | — |
| Anthropic | `anthropic` | — |
| Google | `google` | — |
| Hugging Face | `huggingface` | `base_url` can override the inference endpoint |
| Ollama | `ollama` | `base_url` defaults to `http://localhost:11434/v1` |
| OpenRouter | `openrouter` | `base_url` sets the app URL |
| DeepSeek | `deepseek` | — |

## Template data

When a rule triggers, clickagentic adds a `clickagentic` key to the template context with the following fields:

| Field | Type | Description |
|---|---|---|
| `summary` | `string` | Short summary of the alert |
| `severity` | `string` | Assessed severity: `Critical`, `High`, `Medium`, or `Low` |
| `confidence` | `integer` | Confidence score from 0 to 100 |
| `false_positive_score` | `integer` | Likelihood of a false positive from 0 (unlikely) to 100 (certain) |
| `explanation` | `string` | Detailed explanation of the assessment |
| `mitigations` | `string[]` | List of recommended mitigation actions |

You can reference this data in any webhook template:

```
Alert: {{ rule.name }}
Severity: {{ clickagentic.severity }} (confidence: {{ clickagentic.confidence }}%)
False-positive score: {{ clickagentic.false_positive_score }}%

{{ clickagentic.summary }}

{{ clickagentic.explanation }}

Mitigations:
{% for m in clickagentic.mitigations %}- {{ m }}
{% endfor %}
```

## Examples

### OpenAI

```yaml
plugins:
    clickagentic:
        provider: openai
        model: gpt-4o-mini
        token: sk-...
```

### Anthropic

```yaml
plugins:
    clickagentic:
        provider: anthropic
        model: claude-haiku-4-5-20251001
        token: sk-ant-...
```

### Ollama (local)

```yaml
plugins:
    clickagentic:
        provider: ollama
        model: llama3.2
        token: ollama
        base_url: http://localhost:11434/v1
```

### DeepSeek with false-positive context and extended thinking

```yaml
plugins:
    clickagentic:
        provider: deepseek
        model: deepseek-reasoner
        token: sk-...
        think: true
        false_positive: |
            Scanner 10.0.0.5 runs daily vulnerability scans and will trigger
            port-scan rules. Ignore alerts where source_ip is 10.0.0.5.
```
