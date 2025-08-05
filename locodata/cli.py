"""Command‑line interface."""
import typer
from pathlib import Path
from typing import List

from .config import REPO_PATH
from .design_processor import DesignProcessor
from .codeqa_processor import BaseQAProcessor, CodeQADatasetProcessor, LocalRepoQAProcessor
from . import utils

app = typer.Typer(add_help_option=True)


@app.command()
def scan():
    """Index repository and report basic stats."""
    builder = DesignProcessor(REPO_PATH)
    files = list(builder.iter_code_chunks())
    print(f"Files: {len(list(utils.walk_code_files(REPO_PATH)))} | Chunks: {len(files)}")


@app.command()
def design(requirement: str = typer.Argument(..., help="Requirement in natural language")):
    """Generate a design proposal (design.json)."""
    d = DesignProcessor(REPO_PATH).build_design(requirement)
    print("design.json written under artifacts/.\n", d)


@app.command()
def answer_codeqa_dataset(
    limit: int = typer.Option(None, help="Limit number of examples to process")
):
    """Generate answers for CodeQA dataset (existing code + question pairs)."""
    processor = CodeQADatasetProcessor(REPO_PATH)
    results = processor.process_qa(limit)
    print(f"Processed {len(results)} examples from {REPO_PATH}")


@app.command()
def generate_qa(
    limit: int = typer.Option(None, help="Limit number of code chunks to process")
):
    """Generate both questions and answers for local repository code chunks."""
    processor = LocalRepoQAProcessor(REPO_PATH)
    results = processor.process_qa(limit)
    print(f"Processed {len(results)} code chunks from {REPO_PATH}")


@app.command()
def answer_codeqa(
    code: str = typer.Argument(..., help="Code snippet"),
    question: str = typer.Argument(..., help="Question about the code")
):
    """Generate answer and reasoning for a single code-question pair."""
    
    processor = BaseQAProcessor()
    result = processor.process_qa(code, question)
    
    print(f"\nQuestion: {question}")
    print(f"Code:\n{code}")
    print(f"\nAnswer: {result['answer']}")
    print(f"\nReasoning:\n{result['reasoning']}")
    

@app.command()
def interactive_answer_codeqa():
    """Interactive mode for providing code and asking questions."""
    processor = BaseQAProcessor()
    
    print("=== Interactive Code QA Mode ===")
    print("Enter your code (press Enter twice to finish):")
    
    code_lines = []
    while True:
        line = input()
        if line == "" and code_lines and code_lines[-1] == "":
            break
        code_lines.append(line)
    
    # Remove the last empty line
    code = "\n".join(code_lines[:-1])
    
    print(f"\nCode entered:\n{code}")
    
    questions = []
    print("\nEnter your questions (one per line, press Enter twice to finish):")
    while True:
        question = input("Question: ")
        if question == "":
            break
        questions.append(question)
    
    if not questions:
        print("No questions provided. Exiting.")
        return
    
    print(f"\nProcessing {len(questions)} questions...")
    results = processor.process_qa(selected_code=code, questions=questions)
    
    print(f"\nResults:")
    for i, result in enumerate(results, 1):
        print(f"\n--- Question {i}: {result['question']} ---")
        print(f"Answer: {result['generated_answer']}")
        print(f"Reasoning: {result['reasoning']}")


