"""Utility helpers: code loading, chunking, basic token utils."""
from __future__ import annotations

import ast
from itertools import islice
from pathlib import Path
from typing import Iterable, List, Tuple

from .config import REPO_PATH

CHUNK_SIZE = 2000  # characters
OVERLAP = 200      # characters


def detect_file_language(file_path: Path) -> str:
    """Detect programming language based on file extension."""
    extension = file_path.suffix.lower()
    
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
        '.php': 'php',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.r': 'r',
        '.m': 'matlab',
        '.sh': 'bash',
        '.sql': 'sql',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.xml': 'xml',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.toml': 'toml',
        '.ini': 'ini',
        '.cfg': 'ini',
        '.conf': 'ini',
        '.md': 'markdown',
        '.txt': 'text',
    }
    
    return language_map.get(extension, 'unknown')


def walk_code_files(root: Path = REPO_PATH) -> Iterable[Path]:
    """Yield all code files under *root* based on common programming language extensions."""
    code_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.cs', 
        '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.r', '.m',
        '.sh', '.sql', '.html', '.css', '.scss', '.sass', '.xml', '.json',
        '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.md', '.txt'
    }
    
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in code_extensions:
            yield p


def chunk_code(code: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> List[str]:
    """Naïvely split *code* into overlapping chunks at *chunk_size* chars."""
    chunks: List[str] = []
    i = 0
    while i < len(code):
        chunk = code[i : i + chunk_size]
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


def ast_functions(code: str) -> List[Tuple[str, int, int]]:
    """Return list of (func_name, lineno_start, lineno_end)."""
    funcs = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                end_line = max(getattr(node, "end_lineno", node.lineno), node.lineno)
                funcs.append((node.name, node.lineno, end_line))
    except SyntaxError:
        pass  # ignore broken files
    return funcs
