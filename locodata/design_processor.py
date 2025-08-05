"""Pipeline orchestrator that ties everything together."""
from __future__ import annotations

import json
from pathlib import Path

from . import llm, utils
from .config import ARTIFACTS_DIR, SYSTEM_DESIGN_PROMPT


class DesignProcessor:
    """Design processor for generating design proposals."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    def build_design(self, requirement: str):
        design = self.generate_design(requirement, self.repo_path)
        (ARTIFACTS_DIR / "design.json").write_text(json.dumps(design, indent=2), encoding="utf-8")
        return design

    def repository_overview(self) -> str:
        """Return a high‑level description of the repo with multi-language support."""
        
        # Count files by language
        language_counts = {}
        total_files = 0
        
        for file in utils.walk_code_files(self.repo_path):
            lang = utils.detect_file_language(file)
            language_counts[lang] = language_counts.get(lang, 0) + 1
            total_files += 1
        
        # Build description
        if not language_counts:
            return f"Repository {self.repo_path.name} with no detected code files."
        
        lang_desc = []
        for lang, count in sorted(language_counts.items(), key=lambda x: x[1], reverse=True):
            lang_desc.append(f"{count} {lang} files")
        
        return f"Repository {self.repo_path.name} with {total_files} total code files: {', '.join(lang_desc)}."


    def generate_design(self, requirement: str) -> Dict:
        prompt = (
            f"REQUIREMENT:\n{requirement}\n\nREPO OVERVIEW:\n{self.repository_overview(self.repo_path)}"
        )
        raw = llm.llm_completion(prompt, SYSTEM_DESIGN_PROMPT)
        
        return json.loads(raw)

