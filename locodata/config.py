"""Central configuration and constants."""
from pathlib import Path
import os

# Base paths -----------------------------------------------------
PROJECT_ROOT: Path = Path(os.getenv("LOCODATA_PROJECT_ROOT", Path.cwd()))
REPO_PATH: Path = PROJECT_ROOT / os.getenv("REPO_PATH", "locodata")
ARTIFACTS_DIR: Path = PROJECT_ROOT / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

# Model + provider params ---------------------------------------
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "qwen")
MODEL_NAME: str = os.getenv("LLM_MODEL", "qwen-turbo")
MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", 4096))
TEMPERATURE: float = float(os.getenv("LLM_TEMP", 0.2))
    
# System language -----------------------------------------------
SYSTEM_LANG: str = os.getenv("SYSTEM_LANG", "cn")

# API Key ------------------------------------------------------
API_KEY: str = os.getenv("API_KEY", "")

# System prompts ------------------------------------------------
SYSTEM_ANSWER_PROMPT_EN = (
    "You are an expert software developer. Given a code snippet and a question about it, "
    "provide (1) a concise ANSWER and (2) step-by-step REASONING explaining your answer. "
    "Format strictly as JSON with keys: answer, reasoning."
)

SYSTEM_ANSWER_PROMPT_CN = (
    "你是一个资深软件开发者。给定一段代码片段和关于它的一个问题，"
    "请提供（1）简洁明了的回答；（2）逐步的推理过程来解释你的答案。"
    "请严格按照 JSON 格式输出，包含键名：answer、reasoning。"
)

SYSTEM_GENERATE_PROMPT_EN = (
    "You are an expert software architect. Given a code snippet and its file path, "
    "produce (1) a QUESTION a developer might ask and (2) a concise ANSWER. "
    "Then output a step-by-step reasoning trace. Format strictly as JSON with "
    "keys: question, answer, reasoning."
)

SYSTEM_GENERATE_PROMPT_CN = (
    "你是一个资深软件架构师。给定一段代码片段及其文件路径，"
    "请生成（1）开发者可能会提出的一个问题；（2）简洁明了的回答。"
    "然后输出逐步的推理过程。"
    "请严格按照 JSON 格式输出，包含键名：question、answer、reasoning。"
)

SYSTEM_DESIGN_PROMPT_EN = (
    "You are a senior backend engineer. Given a natural‑language REQUIREMENT and a "
    "brief description of the target repository's architecture, output a JSON with "
    "keys: design (detailed design proposal), reasoning (step‑by‑step chain of "
    "thought)."
)

SYSTEM_DESIGN_PROMPT_CN = (
    "你是一名资深后端工程师。给定一个自然语言需求和目标仓库架构的简要描述，"
    "请输出一个 JSON，包含键名：design（详细设计方案）、reasoning（逐步推理过程）。"
)


if SYSTEM_LANG == "cn":
    SYSTEM_GENERATE_PROMPT = SYSTEM_GENERATE_PROMPT_CN
    SYSTEM_ANSWER_PROMPT = SYSTEM_ANSWER_PROMPT_CN
    SYSTEM_DESIGN_PROMPT = SYSTEM_DESIGN_PROMPT_CN
else:
    SYSTEM_GENERATE_PROMPT = SYSTEM_GENERATE_PROMPT_EN
    SYSTEM_ANSWER_PROMPT = SYSTEM_ANSWER_PROMPT_EN
    SYSTEM_DESIGN_PROMPT = SYSTEM_DESIGN_PROMPT_EN
    