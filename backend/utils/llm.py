import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"
DEFAULT_ZHIPU_MODEL = "glm-4-flash-250414"
DEFAULT_MOONSHOT_MODEL = "moonshot-v1-8k"
CTYUN_DEEPSEEK_BASE_URL = "https://wishub-x6.ctyun.cn/v1"
CTYUN_DEEPSEEK_MODEL = "24625803b01f4f90b72abbe9d9cdf5cc"


def _first_env(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def _normalize_openai_base(url: str) -> str:
    normalized = url.strip().rstrip("/")
    if normalized.endswith("/chat/completions"):
        return normalized[: -len("/chat/completions")]
    if normalized.endswith("/responses"):
        return normalized[: -len("/responses")]
    return normalized


@lru_cache(maxsize=1)
def get_llm_config() -> dict:
    api_key = _first_env("ZAI_API_KEY", "ZHIPU_API_KEY", "OPENAI_API_KEY")
    api_base = _normalize_openai_base(_first_env(
        "ZAI_API_BASE",
        "ZHIPU_API_BASE",
        "OPENAI_API_BASE",
        "OPENAI_BASE_URL",
    ) or ZHIPU_BASE_URL)

    default_model = (
        DEFAULT_MOONSHOT_MODEL if "moonshot" in api_base.lower() else DEFAULT_ZHIPU_MODEL
    )
    model = _first_env(
        "LLM_MODEL",
        "ZAI_MODEL",
        "ZHIPU_MODEL",
        "OPENAI_MODEL",
    ) or default_model

    return {
        "api_key": api_key,
        "api_base": api_base,
        "model": model,
    }


def _build_llm(config: dict, *, temperature: float = 0.7, model_kwargs: dict | None = None) -> ChatOpenAI:
    if not config["api_key"]:
        raise ValueError(
            "Missing LLM API key. Set one of ZAI_API_KEY, ZHIPU_API_KEY, or OPENAI_API_KEY."
        )

    return ChatOpenAI(
        model_name=config["model"],
        openai_api_key=config["api_key"],
        openai_api_base=config["api_base"],
        temperature=temperature,
        model_kwargs=model_kwargs or {},
    )


def build_chat_llm(*, temperature: float = 0.7) -> ChatOpenAI:
    return _build_llm(get_llm_config(), temperature=temperature)


@lru_cache(maxsize=1)
def get_deepseek_config() -> dict:
    api_key = _first_env(
        "DEEPSEEK_API_KEY",
        "CTYUN_APP_KEY",
        "CTYUN_API_KEY",
    )
    api_base = _normalize_openai_base(_first_env(
        "DEEPSEEK_API_BASE",
        "CTYUN_API_BASE",
        "CTYUN_BASE_URL",
    ) or CTYUN_DEEPSEEK_BASE_URL)
    model = _first_env(
        "DEEPSEEK_MODEL",
        "CTYUN_MODEL",
    ) or CTYUN_DEEPSEEK_MODEL

    return {
        "api_key": api_key,
        "api_base": api_base,
        "model": model,
    }


def build_deepseek_chat_llm(*, temperature: float = 0.7, enable_thinking: bool = False) -> ChatOpenAI:
    config = get_deepseek_config()
    if not config["api_key"]:
        raise ValueError(
            "Missing DeepSeek API key. Set DEEPSEEK_API_KEY or CTYUN_APP_KEY."
        )

    # Tianyi Cloud's OpenAI-compatible chat endpoint follows the standard
    # `chat.completions.create(model=..., messages=..., stream=...)` shape.
    # Passing custom fields like `enable_thinking` is rejected by the SDK/client.
    # Keep the argument for call-site compatibility, but do not forward it.
    _ = enable_thinking
    return _build_llm(config, temperature=temperature)
