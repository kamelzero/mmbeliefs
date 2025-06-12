# MMBeliefs (Multimodal Beliefs LLM Benchmark Task)

**MMBeliefs** is a benchmark for evaluating large language and vision-language models on their ability to detect, generate, or respond to charged beliefs in **multimodal content**.

## Overview

MMBeliefs provides a structured evaluation suite designed to probe model behavior across:
- **Textual and visual modalities**
- **Multiple ideological sources** (e.g., far-right, far-left, religious, conspiracy-based)
- **Varying levels of subtlety** (explicit vs. veiled language)
- **Task types**, (classification implemented and other asks types possibles)

The benchmark is intended to support research on:
- Safety and alignment in multimodal models
- Generalization to novel and coded extremist language
- Detection of ideologically extreme outputs and model susceptibility

## Key Features

- **Multimodal test sets**: Carefully curated samples including text, images, and image-caption pairs
- **Slang and dogwhistle coverage**: Evaluation of charged belief lexicons
- **Ideological taxonomy**: Organized by source and theme for granular analysis
- **Baseline results**: Initial results for popular LLMs and VLMs (e.g., GPT-4, Claude, LLaVA)

## Development Requirements

- Python 3.11.8
- Firefox browser
- Git
- pyenv (for Python version management)
- Access to various API services (OpenAI, Anthropic, Google, etc.)

## Installation

### 1. System Dependencies

Install Firefox browser:
```bash
sudo apt update
sudo apt install firefox
```

### 2. Python Environment Setup

Install pyenv (if not already installed):
```bash
curl -fsSL https://pyenv.run | bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc
```

Set up Python environment:
```bash
pyenv install 3.11.8
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### 3. Environment Variables

Add the following to your `~/.bashrc`:
```bash
export HF_TOKEN="your_huggingface_token"
export GROQ_API_KEY="your_groq_key"
export GOOGLE_API_KEY="your_google_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
export OPENAI_API_KEY="your_openai_key"
```

Then run:
```bash
source ~/.bashrc
```

## Data Preparation Pipeline

1. **Scrape Data**
```bash
python3 scrape_data.py
# Outputs: results_with_images.json and images/
```

2. **Standardize Images**
```bash
python3 standardize_images.py
# Outputs: results_with_images_std.json and images_std/
```

3. **Generate Task Questions**
```bash
python3 generate_questions.py
# Outputs: task_data_fc.json
```

4. **Create HuggingFace Dataset**
```bash
python3 create_hfdataset.py
# Pushes mmbeliefs_mcq to your HF account
```

## Testing

Run the test suite to ensure everything is working correctly:
```bash
# Run all tests
pytest

# Run specific test files
pytest test_image_labels.py
pytest test_standardize_images.py
```

## Evaluation Setup

### 1. Set up lmms-eval

Clone and install lmms-eval:
```bash
git clone https://github.com/EvolvingLMMs-Lab/lmms-eval
cd lmms-eval
# Follow development install directions from: https://github.com/EvolvingLMMs-Lab/lmms-eval/
```

### 2. Configure Evaluation Files

Copy necessary files:
```bash
# Copy model runner
cp lmms-eval-files/mmbeliefs_mcq.py lmms-eval/examples/models/

# Copy task files
cp -r mmbeliefs_mcq lmms-eval/lmms-eval/tasks/
```

Important: Update the HuggingFace dataset path in:
`lmms-eval-files/mmbeliefs_mcq/_default_template_fringe_yaml`

### 3. Run Evaluation

Execute the benchmark:
```bash
python3 lmms-eval/examples/models/mmbeliefs_mcq.py
```

## Known Issues and Notes

- Gemini 2.5 models require very high max_new_tokens; see lmms-eval-files/NOTES.md for suggested approach.
- The evaluation process requires valid API keys for all services
- Ensure sufficient disk space for image storage and processing

## Contributing

Please refer to our contributing guidelines for information on how to submit issues, feature requests, and pull requests.

## License

[Add license information here]
