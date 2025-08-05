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
    """Smart code chunking that respects code structure and creates meaningful chunks."""
    if len(code) <= chunk_size:
        return [code]
    
    # Strategy 1: Try to chunk by complete functions/classes (for Python)
    if 'def ' in code or 'class ' in code:
        chunks = _chunk_by_functions(code, chunk_size, overlap)
        if chunks and all(len(chunk) <= chunk_size for chunk in chunks):
            return chunks
    
    # Strategy 2: Try to chunk by complete statements/blocks
    chunks = _chunk_by_statements(code, chunk_size, overlap)
    if chunks and all(len(chunk) <= chunk_size for chunk in chunks):
        return chunks
    
    # Strategy 3: Try to chunk by lines (respecting line boundaries)
    chunks = _chunk_by_lines(code, chunk_size, overlap)
    if chunks and all(len(chunk) <= chunk_size for chunk in chunks):
        return chunks
    
    # Fallback: Original naive chunking
    return _naive_chunk(code, chunk_size, overlap)


def _chunk_by_functions(code: str, chunk_size: int, overlap: int) -> List[str]:
    """Chunk code by complete functions and classes."""
    try:
        tree = ast.parse(code)
        chunks = []
        current_chunk = ""
        
        # Collect all function and class definitions
        code_units = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                unit_code = ast.unparse(node)
                # If a single unit is too large, skip function-based chunking
                if len(unit_code) > chunk_size:
                    return []
                code_units.append(unit_code)
        
        # If no functions/classes found, return empty to try other strategies
        if not code_units:
            return []
        
        # Build chunks from code units
        for unit in code_units:
            # If adding this unit would exceed chunk size and we have content
            if len(current_chunk) + len(unit) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap
                if overlap > 0:
                    overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                    current_chunk = overlap_text + "\n\n" + unit
                else:
                    current_chunk = unit
            else:
                current_chunk += "\n\n" + unit if current_chunk else unit
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else []
    except SyntaxError:
        # If AST parsing fails, fall back to statement-based chunking
        return []


def _chunk_by_statements(code: str, chunk_size: int, overlap: int) -> List[str]:
    """Chunk code by complete statements, respecting indentation and logical blocks."""
    lines = code.split('\n')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for line in lines:
        line_size = len(line) + 1  # +1 for newline
        
        # If adding this line would exceed chunk size and we have content
        if current_size + line_size > chunk_size and current_chunk:
            # Complete the current chunk
            chunk_text = '\n'.join(current_chunk)
            chunks.append(chunk_text)
            
            # Start new chunk with overlap
            if overlap > 0:
                overlap_lines = []
                overlap_size = 0
                for overlap_line in reversed(current_chunk):
                    if overlap_size + len(overlap_line) + 1 <= overlap:
                        overlap_lines.insert(0, overlap_line)
                        overlap_size += len(overlap_line) + 1
                    else:
                        break
                current_chunk = overlap_lines
                current_size = overlap_size
            else:
                current_chunk = []
                current_size = 0
        
        current_chunk.append(line)
        current_size += line_size
    
    # Add the last chunk
    if current_chunk:
        chunk_text = '\n'.join(current_chunk)
        chunks.append(chunk_text)
    
    return chunks


def _chunk_by_lines(code: str, chunk_size: int, overlap: int) -> List[str]:
    """Chunk code by complete lines, ensuring we don't break in the middle of lines."""
    lines = code.split('\n')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for line in lines:
        line_size = len(line) + 1  # +1 for newline
        
        # If adding this line would exceed chunk size
        if current_size + line_size > chunk_size and current_chunk:
            # Complete the current chunk
            chunk_text = '\n'.join(current_chunk)
            chunks.append(chunk_text)
            
            # Start new chunk with overlap
            if overlap > 0:
                overlap_lines = []
                overlap_size = 0
                for overlap_line in reversed(current_chunk):
                    if overlap_size + len(overlap_line) + 1 <= overlap:
                        overlap_lines.insert(0, overlap_line)
                        overlap_size += len(overlap_line) + 1
                    else:
                        break
                current_chunk = overlap_lines
                current_size = overlap_size
            else:
                current_chunk = []
                current_size = 0
        
        current_chunk.append(line)
        current_size += line_size
    
    # Add the last chunk
    if current_chunk:
        chunk_text = '\n'.join(current_chunk)
        chunks.append(chunk_text)
    
    return chunks


def _naive_chunk(code: str, chunk_size: int, overlap: int) -> List[str]:
    """Original naive chunking as fallback."""
    chunks = []
    i = 0
    while i < len(code):
        chunk = code[i : i + chunk_size]
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

