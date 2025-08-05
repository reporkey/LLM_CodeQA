"""LLM‑powered Q&A generation for code chunks."""
from __future__ import annotations

from .config import MODEL_NAME, TEMPERATURE, API_KEY, LLM_PROVIDER

try:
    import openai  # noqa: I900
    openai.api_key = API_KEY
    openai.base_url = None
    if LLM_PROVIDER == "qwen":
        openai.base_url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/"
    elif LLM_PROVIDER == "openai":
        openai.base_url = "https://api.openai.com/v1"
    
except ImportError:  # pragma: no cover
    openai = None


def llm_completion(prompt: str, system_prompt: str) -> str:
    """Call the configured LLM provider and return raw text."""
    if openai is None:
        raise RuntimeError("openai package not installed. Run `pip install openai`.")
    response = openai.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": prompt}],
        temperature=TEMPERATURE,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()
