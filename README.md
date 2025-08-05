# Locodata – Intelligent Training Data Generator for Local Codebases

Locodata automates the creation of **Q&A pairs** and **design‑plan traces** from a local Git repository so that you can fine‑tune models like Qwen‑7B or GPT‑J for internal knowledge.

## Quick Start

### Installation

```bash
# 1. Install dependencies using conda
mamba env create -f environment.yml
conda activate hsbc

# 2. Point REPO_PATH to your repo to analyze (optional, defaults to ./)
export REPO_PATH=/path/to/your/codebase

# 3. Set up your API key (OpenAI or Qwen)
export API_KEY=your_api_key_here

# 4. Set language
export SYSTEM_LANG=cn
```

### Basic Usage

```bash
# Scan repository and report stats
python -m locodata scan

# Generate a design proposal
python -m locodata design "Add async support with retries"

# Generate QA pairs from your codebase
python -m locodata generate_qa --limit 10

# Generate answers for CodeQA dataset
python -m locodata answer_codeqa_dataset --limit 10

# Generate answer for a single code-question pair
python -m locodata answer_codeqa "def hello(): return 'world'" "What does this function return?"

# Iterative mode for code-question pair answering
python -m locodata interactive_answer_codeqa
```

Artifacts land in `./artifacts/`:

* **qa.jsonl** – ready for supervised fine‑tuning (JSONL with columns `id,question,answer,code,reasoning,file_path,start_line,end_line`)
* **design.json** – detailed design with reasoning trace
* **codeqa_*_results.json** – CodeQA dataset results with generated answers and reasoning

## Getting API Keys

### OpenAI Setup
1. **Get API Key**: Visit https://platform.openai.com/api-keys
2. **Set Environment Variable**: `export API_KEY=your_api_key_here`
```bash
export LLM_PROVIDER=openai
export MODEL_NAME=gpt-4o-mini
export API_KEY=your_openai_api_key
```

### Qwen Setup
1. **Visit the DashScope Console**: Go to https://dashscope.console.aliyun.com/
2. **Sign up/Login**: Create an Alibaba Cloud account or log in
3. **Navigate to API Keys**: Find the API Keys section in the console
4. **Create API Key**: Generate a new API key (should start with `sk-`)
5. **Set Environment Variable**: `export API_KEY=your_api_key_here`
```bash
export LLM_PROVIDER=qwen
export MODEL_NAME=qwen-turbo
export API_KEY=your_qwen_api_key
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM provider to use (`openai` or `qwen`) | `qwen` |
| `LLM_MODEL` | OpenAI model name | `qwen-turbo` |
| `API_KEY` | API key | ` ` |
| `TEMPERATURE` | Temperature for generation | `0.2` |
| `MAX_TOKENS` | Maximum tokens for generation | `4096` |
| `LOCODATA_REPO` | Path to repository to analyze | `./` |
| `LOCODATA_PROJECT_ROOT` | Project root directory | Current working directory |
| `SYSTEM_LANG` | System language  | `cn` |

## Testing and Examples

- **CLI Commands**: Use `python -m locodata --help` for available commands


## CodeQA Dataset Support

The project now supports processing the CodeQA dataset for generating answers given code and questions:

### CodeQA Dataset Structure
```
CodeQA_data/
├── python/
│   ├── train/
│   │   ├── train.code
│   │   ├── train.question
│   │   └── train.answer
│   ├── dev/
│   └── test/
└── java/
    ├── train/
    ├── dev/
    └── test/
```

https://github.com/jadecxliu/CodeQA?tab=readme-ov-file

- Liu, Chenxiao, and Xiaojun Wan. **CodeQA: A Question Answering Dataset for Source Code Comprehension.** In *Findings of the Association for Computational Linguistics: EMNLP 2021*, pages 2618–2632, 2021.
