"""CodeQA dataset processor for generating answers given code and questions."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Iterator
from tqdm import tqdm

from . import llm, utils
from .config import ARTIFACTS_DIR, SYSTEM_GENERATE_PROMPT, SYSTEM_ANSWER_PROMPT


class BaseQAProcessor:
    """Base class for QA processing functionality."""
    def __init__(self):
        pass
    
    def process_qa(self, code: str, question: str) -> Dict:
        """Process a single code-question pair."""
        try:
            payload = f"CODE:\n```\n{code}\n```\nQUESTION: {question}\n"
            raw = llm.llm_completion(payload, SYSTEM_ANSWER_PROMPT)
            raw = json.loads(raw)
            
            result = {
                "code": code,
                "question": question,
                "mode": "single_qa",
                "generated_answer": raw.get("answer"),
                "reasoning": raw.get("reasoning")
            }
            return result
            
        except Exception as e:
            return {
                "code": code,
                "question": question,
                "mode": "single_qa",
                "generated_answer": None,
                "reasoning": None,
                "error": str(e)
            }

    def process_multiple_qa(self, code: str, questions: List[str]) -> List[Dict]:
        """Process code with multiple user-provided questions."""
        results = []
        
        for i, question in enumerate(tqdm(questions, desc=f"Processing questions for selected code", unit="question")):
            result = self.process_qa(code, question)
            result["question_index"] = i + 1
            results.append(result)
            
        return results

    def save_results(self, results: List[Dict], output_file: Path):
        """Save results to JSON file."""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to {output_file}")


class CodeQADatasetProcessor(BaseQAProcessor):
    """Process CodeQA dataset and generate answers for code-question pairs."""

    def __init__(self, data_dir: Path):
        super().__init__()
        self.data_dir = data_dir
            
    def iter_codeqa_data(self) -> Iterator[Dict]:
        """Iterate through CodeQA data files."""
        
        # Extract split name from the directory path
        split_name = self.data_dir.name
        
        code_file = self.data_dir / f"{split_name}.code"
        question_file = self.data_dir / f"{split_name}.question"
        answer_file = self.data_dir / f"{split_name}.answer"
        
        if not all(f.exists() for f in [code_file, question_file, answer_file]):
            raise FileNotFoundError(f"Required files not found in {self.data_dir}")
        
        with open(code_file, 'r', encoding='utf-8') as cf, \
             open(question_file, 'r', encoding='utf-8') as qf, \
             open(answer_file, 'r', encoding='utf-8') as af:
            
            for line_num, (code_line, question_line, answer_line) in enumerate(
                zip(cf, qf, af), 1
            ):
                yield {
                    "line_num": line_num,
                    "code": code_line.strip(),
                    "question": question_line.strip(),
                    "ground_truth_answer": answer_line.strip(),
                    "split": split_name,
                    "language": self.data_dir.parent.name,
                    "mode": "codeqa_data"
                }

    def process_qa(self, limit: int):
        """Process code-question pairs from CodeQA dataset."""
        
        results = []
        
        for i, data in enumerate(tqdm(self.iter_codeqa_data(), 
                                    desc=f"Generating answers for CodeQA dataset {self.data_dir}", 
                                    unit="pair")):
            if limit and i >= limit:
                break
                
            try:
                # For CodeQA data, we have both code and question
                payload = f"CODE:\n```\n{data['code']}\n```\nQUESTION: {data['question']}\n"
                raw = llm.llm_completion(payload, SYSTEM_ANSWER_PROMPT)
                raw = json.loads(raw)
            
                # Combine original data with generated answer
                result = {
                    **data,
                    "generated_answer": raw.get("answer"),
                    "reasoning": raw.get("reasoning")
                }
                results.append(result)
                
            except Exception as e:
                print(f"Error processing item {i+1}: {e}")
                # Add error info to results
                result = {
                    **data,
                    "generated_answer": None,
                    "reasoning": None,
                    "error": str(e)
                }
                results.append(result)
        
        # Save results with appropriate naming
        split_name = self.data_dir.name
        language = self.data_dir.parent.name
        output_file = ARTIFACTS_DIR / f"codeqa_{language}_{split_name}_results.json"
        self.save_results(results, output_file)
        
        return results


class LocalRepoQAProcessor(BaseQAProcessor):
    """Process local repository code chunks and generate both questions and answers."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
            
    def iter_code_chunks(self) -> Iterator[dict]:
        """Iterate through code chunks from local repository files."""
        for file in utils.walk_code_files(self.repo_path):
            code = file.read_text(errors="ignore")
            chunks = utils.chunk_code(code)
            file_lang = utils.detect_file_language(file)
            for idx, chunk in enumerate(chunks):
                yield {
                    "code": chunk,
                    "file_path": str(file),
                    "file_lang": file_lang,
                    "start_line": idx * (utils.CHUNK_SIZE - utils.OVERLAP) + 1,
                    "end_line": idx * (utils.CHUNK_SIZE - utils.OVERLAP) + len(chunk.splitlines()),
                    "mode": "local_repo"
                }

    def process_qa(self, limit: int):
        """Process local repository code chunks and generate both questions and answers."""
        
        results = []
        
        for i, data in enumerate(tqdm(self.iter_code_chunks(), 
                                    desc=f"Generating Q&A for local repo {self.repo_path}", 
                                    unit="chunk")):
            if limit and i >= limit:
                break
                
            try:
                # For local repo, we need to generate both question and answer
                payload = f"CODE:\n```\n{data['code']}\n```\nFILE_LANG: {data['file_lang']}\nSTART_LINE: {data['start_line']}\nEND_LINE: {data['end_line']}\n"
                raw = llm.llm_completion(payload, SYSTEM_GENERATE_PROMPT)
                raw = json.loads(raw)
            
                # Combine original data with generated answer
                result = {
                    **data,
                    "generated_answer": raw.get("answer"),
                    "generated_question": raw.get("question"),
                    "reasoning": raw.get("reasoning")
                }
                results.append(result)
                
            except Exception as e:
                print(f"Error processing item {i+1}: {e}")
                # Add error info to results
                result = {
                    **data,
                    "generated_answer": None,
                    "generated_question": None,
                    "reasoning": None,
                    "error": str(e)
                }
                results.append(result)
        
        # Save results with appropriate naming
        output_file = ARTIFACTS_DIR / f"local_repo_qa_results.json"
        self.save_results(results, output_file)
        
        return results
