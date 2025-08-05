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
        design = self.generate_design(requirement)
        (ARTIFACTS_DIR / "design.json").write_text(json.dumps(design, indent=2), encoding="utf-8")
        return design

    def repository_overview(self) -> str:
        """Return a comprehensive description of the repo architecture for design generation."""
        
        # Count files by language
        language_counts = {}
        total_files = 0
        file_sizes = []
        
        for file in utils.walk_code_files(self.repo_path):
            lang = utils.detect_file_language(file)
            language_counts[lang] = language_counts.get(lang, 0) + 1
            total_files += 1
            try:
                file_sizes.append(file.stat().st_size)
            except:
                pass
        
        # Analyze project structure
        structure_info = self._analyze_project_structure()
        
        # Detect technology stack
        tech_stack = self._detect_technology_stack()
        
        # Build comprehensive description
        if not language_counts:
            return f"Repository {self.repo_path.name} with no detected code files."
        
        lang_desc = []
        for lang, count in sorted(language_counts.items(), key=lambda x: x[1], reverse=True):
            lang_desc.append(f"{count} {lang} files")
        
        avg_file_size = sum(file_sizes) / len(file_sizes) if file_sizes else 0
        
        overview = f"""Repository: {self.repo_path.name}
                    Total Files: {total_files} ({', '.join(lang_desc)})
                    Average File Size: {avg_file_size:.0f} bytes

                    Project Structure:
                    {structure_info}

                    Technology Stack:
                    {tech_stack}"""
        
        return overview

    def _analyze_project_structure(self) -> str:
        """Analyze and describe the project's directory structure."""
        structure = []
        
        # Look for common project files
        config_files = []
        for pattern in ['requirements.txt', 'package.json', 'pom.xml', 'build.gradle', 
                       'Cargo.toml', 'go.mod', 'Gemfile', 'composer.json']:
            if (self.repo_path / pattern).exists():
                config_files.append(pattern)
        
        # Build full directory structure
        structure_lines = []
        structure_lines.append(f"  Root: {self.repo_path.name}/")
        
        def add_directory_contents(path: Path, indent: int = 2):
            """Recursively add directory contents to structure."""
            try:
                items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
                for item in items:
                    # Skip hidden files and directories
                    if item.name.startswith('.'):
                        continue
                    
                    # Skip __pycache__ and other cache directories
                    if item.name in ['__pycache__', 'node_modules', '.git', '.venv', 'venv']:
                        continue
                    
                    prefix = "  " * indent
                    if item.is_dir():
                        structure_lines.append(f"{prefix}📁 {item.name}/")
                        add_directory_contents(item, indent + 1)
                    else:
                        # Get file extension for better categorization
                        ext = item.suffix.lower()
                        if ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.rs']:
                            structure_lines.append(f"{prefix}📄 {item.name}")
                        elif ext in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg']:
                            structure_lines.append(f"{prefix}⚙️  {item.name}")
                        elif ext in ['.md', '.txt', '.rst']:
                            structure_lines.append(f"{prefix}📝 {item.name}")
                        else:
                            structure_lines.append(f"{prefix}📄 {item.name}")
            except PermissionError:
                structure_lines.append(f"{'  ' * indent}❌ Permission denied")
            except Exception as e:
                structure_lines.append(f"{'  ' * indent}❌ Error: {str(e)}")
        
        add_directory_contents(self.repo_path)
        
        structure.append('\n'.join(structure_lines))
        
        # Add configuration files summary
        if config_files:
            structure.append(f"  Configuration files: {', '.join(config_files)}")
        
        return '\n'.join(structure) if structure else "  Standard project structure"

    def _detect_technology_stack(self) -> str:
        """Detect and describe the technology stack."""
        stack_info = []
        
        # Check for framework indicators
        framework_indicators = {
            'Django': ['django', 'manage.py'],
            'Flask': ['flask', 'app.py'],
            'FastAPI': ['fastapi', 'uvicorn'],
            'Express': ['express', 'package.json'],
            'React': ['react', 'jsx', 'tsx'],
            'Vue': ['vue'],
            'Spring': ['spring', 'pom.xml'],
            'Rails': ['rails', 'Gemfile'],
            'Laravel': ['laravel', 'artisan'],
        }
        
        detected_frameworks = []
        for framework, indicators in framework_indicators.items():
            for indicator in indicators:
                if any(indicator in str(f).lower() for f in utils.walk_code_files(self.repo_path)):
                    detected_frameworks.append(framework)
                    break
        
        if detected_frameworks:
            stack_info.append(f"  Frameworks: {', '.join(set(detected_frameworks))}")
        
        # Check for database indicators
        db_indicators = {
            'SQLite': ['.db', '.sqlite'],
            'PostgreSQL': ['postgres', 'psycopg2'],
            'MySQL': ['mysql', 'pymysql'],
            'MongoDB': ['mongo', 'pymongo'],
            'Redis': ['redis'],
        }
        
        detected_dbs = []
        for db, indicators in db_indicators.items():
            for indicator in indicators:
                if any(indicator in str(f).lower() for f in utils.walk_code_files(self.repo_path)):
                    detected_dbs.append(db)
                    break
        
        if detected_dbs:
            stack_info.append(f"  Databases: {', '.join(set(detected_dbs))}")
        
        return '\n'.join(stack_info) if stack_info else "  Standard technology stack"

    def generate_design(self, requirement: str) -> dict:
        """Generate a design proposal for the given requirement."""
        overview = self.repository_overview()
        prompt = (
            f"REQUIREMENT:\n{requirement}\n\nREPO OVERVIEW:\n{overview}"
        )
        raw = llm.llm_completion(prompt, SYSTEM_DESIGN_PROMPT)
        # add the repo overview to the design
        design = json.loads(raw)
        design['requirement'] = requirement
        design["repo_overview"] = overview
        return design

    def iter_code_chunks(self):
        """Iterate through code chunks in the repository."""
        for file_path in utils.walk_code_files(self.repo_path):
            try:
                code = file_path.read_text(encoding='utf-8')
                chunks = utils.chunk_code(code)
                for i, chunk in enumerate(chunks):
                    yield {
                        'file_path': str(file_path),
                        'chunk_index': i,
                        'code': chunk,
                        'language': utils.detect_file_language(file_path)
                    }
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

