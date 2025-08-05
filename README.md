# Locodata – AI-Powered Code Intelligence & Training Data Generator

**Transform your codebase into intelligent training data for custom AI models**

Locodata is a sophisticated code analysis and training data generation platform that automatically extracts knowledge from your codebase to create high-quality Q&A pairs and design proposals. Built for developers who want to fine-tune AI models on their internal code knowledge.

## 🚀 Key Features

### **Smart Code Analysis**
- **Intelligent Chunking**: Advanced code segmentation that respects function boundaries, class structures, and logical blocks
- **Multi-language Support**: Python, JavaScript, TypeScript, Java, C++, Go, Rust, and 20+ programming languages
- **Architecture Detection**: Automatic identification of frameworks, databases, and technology stacks
- **Project Structure Analysis**: Complete directory tree mapping with file categorization

### **AI-Powered Content Generation**
- **Q&A Pair Generation**: Create contextual questions and answers from your codebase
- **Design Proposals**: Generate detailed architectural designs with reasoning traces
- **Interactive Mode**: Real-time code analysis and question answering
- **CodeQA Dataset Support**: Process standard code comprehension datasets for testing

## 🛠️ Technical Architecture

### **Core Components**
- **Design Processor**: Generates architectural proposals with comprehensive repository analysis
- **CodeQA Processor**: Handles Q&A generation for local repositories
- **Smart Chunking Engine**: Multi-strategy code segmentation (function-based, statement-based, line-based)
- **LLM Integration**: Unified interface for multiple AI providers

### **Advanced Features**
- **Repository Overview**: Comprehensive analysis including file statistics, technology stack, and project structure
- **Context-Aware Processing**: Maintains code context across chunks for better AI understanding
- **Error Handling**: Robust processing with graceful fallbacks for malformed code
- **Performance Optimized**: Efficient algorithms for large codebases

## 📊 Output Formats

### **Artifacts Generated**
- `design.json` - Detailed architectural designs with reasoning
- `local_repo_qa_results.json` - Q&A pairs from your codebase
- `codeqa_{language}_{split}_results.json` - Processed CodeQA dataset results

## 🔧 Quick Start

### Installation

```bash
# 1. Install dependencies using conda
mamba env create -f environment.yml
conda activate hsbc

# 2. Configure your repository path
export REPO_PATH=/path/to/your/codebase

# 3. Set up your AI provider
export API_KEY=your_api_key_here
export LLM_PROVIDER=qwen  # or openai
export MODEL_NAME=qwen-turbo

# 4. Set language preference
export SYSTEM_LANG=en  # or cn
```

### Basic Usage

```bash
# Analyze your repository structure
python -m locodata scan

# Generate architectural design for a new feature
python -m locodata design "Add async support with retries"

# Create Q&A pairs from your codebase
python -m locodata generate-qa --limit 10

# Process CodeQA dataset
python -m locodata answer-codeqa-dataset --path CodeQA_data/python/train --limit 10

# Generate answer for a code-question pair
python -m locodata answer-codeqa "def hello(): return 'world'" "What does this function return?"

# Interactive code analysis
python -m locodata interactive-answer-codeqa
```

## 🔗 Integration & Extensibility

### **Supported AI Providers**
- **OpenAI**: GPT-4, GPT-3.5, and other OpenAI models
- **Alibaba Qwen**: Qwen-Turbo, Qwen-Plus, and other Qwen models
- **Extensible**: Easy to add new providers

## 🔑 Getting API Keys

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

## ⚙️ Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM provider to use (`openai` or `qwen`) | `qwen` |
| `LLM_MODEL` | Model name for the selected provider | `qwen-turbo` |
| `API_KEY` | API key for the selected provider | ` ` |
| `TEMPERATURE` | Temperature for generation | `0.2` |
| `MAX_TOKENS` | Maximum tokens for generation | `4096` |
| `REPO_PATH` | Path to repository to analyze | `./` |
| `PROJECT_ROOT` | Project root directory | Current working directory |
| `SYSTEM_LANG` | System language (`en` or `cn`) | `cn` |

## 📚 CodeQA Dataset Support

Locodata supports processing the CodeQA dataset for generating answers given code and questions:

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

**Reference**: Liu, Chenxiao, and Xiaojun Wan. **CodeQA: A Question Answering Dataset for Source Code Comprehension.** In *Findings of the Association for Computational Linguistics: EMNLP 2021*, pages 2618–2632, 2021.

**Dataset**: https://github.com/jadecxliu/CodeQA

## 🧪 Testing and Examples

- **CLI Commands**: Use `python -m locodata --help` for available commands
- **Interactive Mode**: Try `python -m locodata interactive-answer-codeqa` for real-time analysis
- **Batch Processing**: Use `python -m locodata generate-qa --limit 100` for large-scale generate Q&A
