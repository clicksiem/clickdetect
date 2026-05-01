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
    title: str = Field(description="Short, human-readable title summarizing the alert context and main issue detected")
    summary: str = Field(description="One-sentence objective summary explaining what triggered the alert and its immediate significance")
    severity: AlertSeverity = Field(description="Categorical severity level (Critical, High, Medium, Low) based on potential impact and urgency of the detected activity")
    confidence: int = Field(ge=0, le=100, description="Percentage representing how confident the system is (0-100) in the correctness of this assessment based on available evidence. Lower values indicate high uncertainty or incomplete data, while higher values indicate strong and reliable supporting evidence")
    false_positive_score: int = Field(ge=0, le=100, description="Percentage (0-100) estimating the likelihood that this alert is a false positive. A value of 0 indicates high confidence in a true positive, while 100 indicates high confidence that the alert is benign")
    risk_score: int = Field(ge=0, le=100, description="Percentage representing the overall risk level (0-100) considering potential impact and likelihood of threat activity. Higher values indicate more severe and actionable security risk")
    explanation: str = Field(description="Detailed explanation of the alert, including suspected attack vector, affected assets, triggering conditions, and reasoning behind the assessment")
    mitigations: Optional[List[str]] = Field(default=[], description="Ordered list of specific and actionable steps to investigate, contain, or remediate the threat described in this alert")
    affected_entities: Optional[List[str]] = Field(default=None, description="List of affected entities such as users, hosts, IP addresses, or services involved in the alert" )
    recommended_action: Optional[str] = Field(default=None, description="Single most important next action to take in response to this alert (e.g., isolate host, disable user, block IP)")

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
    ids: Optional[List[str]] = None
    from_level: Optional[int] = Field(default=None, ge=1)
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

        if self.config.ids:
            if rule.id in self.config.ids:
                logger.debug(f'skipping rule id {rule.id}')
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
                "clickagentic": analysis.model_dump(mode='json'),
            }
        }
