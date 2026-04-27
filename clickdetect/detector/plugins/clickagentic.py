import json
import logging
from enum import Enum
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.capabilities import Thinking
from pydantic_ai.exceptions import UnexpectedModelBehavior
from typing import Any, List, Optional, cast
from .base import PluginBase
from ..hooks import HookRegistry, EventEnum
from ..manager import Manager

logger = logging.getLogger(__name__)

class AlertSeverity(str, Enum):
    critical = 'Critical'
    high = 'High'
    medium = 'Medium'
    low = 'Low'

class AlertAnalysisResponse(BaseModel):
    summary: str = Field(description="One-sentence objective summary of what the alert represents and why it was triggered")
    severity: AlertSeverity = Field(description="Assessed severity level (Critical, High, Medium, or Low) based on the alert context and potential impact")
    confidence: int = Field(ge=0, le=100, description="Confidence score (0–100) reflecting how certain the analysis is given the available alert data")
    false_positive_score: int = Field(ge=0, le=100, description="Estimated probability (0–100) that this alert is a false positive, where 0 means definitely a true positive and 100 means definitely a false positive")
    explanation: str = Field(description="In-depth explanation of the alert, including attack vector, affected assets, and why the rule was triggered")
    mitigations: List[str] = Field(description="Ordered list of concrete mitigation steps to contain or remediate the threat described in this alert")

class ProviderEnum(str, Enum):
    openai = 'openai'
    anthropic = 'anthropic'
    google = 'google'
    huggingface = 'huggingface'
    ollama = 'ollama'
    openrouter = 'openrouter'
    deepseek = 'deepseek'

class ClickagenticConfig(BaseModel):
    provider: ProviderEnum
    model: str
    token: str
    ids = Optional[List[str]]
    from_level: Optional[int] = Field(ge=1) # only works if the level is >= than from_level
    base_url: Optional[str] = None
    false_positive: Optional[str] = None
    think: bool = Field(False)


class ClickAgenticLLM(PluginBase):
    id = "clickagentic"
    name = "Clickdetect LLM agent"
    version = "v0.0.1"

    system_prompt = """
    You are a cybersecurity analyst agent specialized in triaging alerts from clickdetect, a SIEM alerting system.
    When analyzing an alert, consider the detector context, rule name, severity level, and the raw alert data provided.
    Assess the likelihood of a false positive based on context and provide at least one concrete mitigation step.
    """
    
    def __init__(self, manager: Manager):
        super().__init__(manager)

    async def run(self, config: Any):
        logger.debug("clickagentic")
        logger.debug(config)
        try:
            config = ClickagenticConfig.model_validate(config)
            capa = []
            if config.think:
                capa.append(Thinking())

            system_prompt = self.system_prompt
            if config.false_positive:
                system_prompt += f'\nThis is a base of false positives, generate false positive score based on this\n{config.false_positive}'

            model = self._build_model(config.provider, config.model, config.token, config.base_url)
            agent = Agent(model=model, system_prompt=system_prompt, output_type=AlertAnalysisResponse, output_retries=2, capabilities=capa)
            self.agent = agent
            self.config = config
        except Exception as ex:
            self.active = False
            logger.error('Cant configure plugin')
            logger.error(str(ex))

    def _build_model(self, provider: ProviderEnum, model_name: str, token: str, base_url: str | None = None):
        if provider == ProviderEnum.openai:
            from pydantic_ai.models.openai import OpenAIChatModel
            from pydantic_ai.providers.openai import OpenAIProvider
            return OpenAIChatModel(model_name, provider=OpenAIProvider(base_url=None, api_key=token))

        elif provider == ProviderEnum.anthropic:
            from pydantic_ai.models.anthropic import AnthropicModel
            from pydantic_ai.providers.anthropic import AnthropicProvider
            return AnthropicModel(model_name, provider=AnthropicProvider(api_key=token))

        elif provider == ProviderEnum.google:
            from pydantic_ai.models.google import GoogleModel
            from pydantic_ai.providers.google import GoogleProvider
            return GoogleModel(model_name, provider=GoogleProvider(api_key=token))

        elif provider == ProviderEnum.huggingface:
            from pydantic_ai.models.huggingface import HuggingFaceModel
            from pydantic_ai.providers.huggingface import HuggingFaceProvider
            hf_kwargs = {'api_key': token}
            if base_url:
                hf_kwargs['base_url'] = base_url
            return HuggingFaceModel(model_name, provider=HuggingFaceProvider(**hf_kwargs))

        elif provider == ProviderEnum.ollama:
            from pydantic_ai.models.ollama import OllamaModel
            from pydantic_ai.providers.ollama import OllamaProvider
            return OllamaModel(model_name, provider=OllamaProvider(
                base_url=base_url or 'http://localhost:11434/v1',
                api_key=token or 'ollama',
            ))

        elif provider == ProviderEnum.openrouter:
            from pydantic_ai.models.openrouter import OpenRouterModel
            from pydantic_ai.providers.openrouter import OpenRouterProvider
            return OpenRouterModel(model_name, provider=OpenRouterProvider(
                app_url=base_url or None,
                api_key=token,
            ))
        elif provider == ProviderEnum.deepseek:
            from pydantic_ai.models.openai import OpenAIChatModel
            from pydantic_ai.providers.deepseek import DeepSeekProvider
            return OpenAIChatModel(model_name, provider=DeepSeekProvider(api_key=token))

    async def register_hooks(self, registry: HookRegistry) -> None:
        registry.register(EventEnum.on_rule_triggered, self._handle_rule_triggered)

    async def _handle_rule_triggered(
        self, rule, detector, result, template_data
    ) -> dict | None:

        if self.config.from_level:
            if rule.level < self.config.from_level:
                logger.debug(f'skipping rule {rule.id} analyzis. rule_level: {rule.level} < from_level: {self.config.from_level}')
                return None

        logger.info(
            f"[{detector.name}] Rule triggered: {rule.name} "
            f"(level={rule.level}, count={result.len})"
        )

        if self.agent is None:
            logger.warning("clickagentic agent not configured, skipping LLM analysis")
            return None

        prompt = (
            f"Detector: {detector.name}\n"
            f"Rule: {rule.name} (level={rule.level})\n"
            f"Alert count: {result.len}\n"
            f"Alert data:\n{json.dumps(template_data, default=str, indent=2)}"
        )

        try:
            run_result = await self.agent.run(prompt)
            logger.info(f'usage: {run_result.usage()}')
            analysis  = cast(AlertAnalysisResponse, run_result.output) 
        except UnexpectedModelBehavior as ex:
            logger.error(f"LLM analysis failed after retries for rule '{rule.name}': {ex}")
            return None

        return {
            "template_data": {
                **template_data,
                "clickagentic": analysis.model_dump(),
            }
        }
