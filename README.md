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

## Install

Install firefox, if not already installed.
```
sudo apt update
sudo apt install firefox
```

Install pyenv, if not already installed.
```
curl -fsSL https://pyenv.run | bash
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
```

```
pyenv install 3.11.8
pyenv virtualenv 3.11.8 mmbeliefs-311
pyenv activate mmbeliefs-311
```

```
python3.11 -m venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

# Preparing Data

Scrape data from the web. This outputs results_with_images.json and images files under images/.
```
python3 scrape_data.py
```

Standardize the images. By default, this outputs results_with_images_std.json and images_std/.
```
python3 standardize_images.py
```

Generate task data questions from the scraped data. This outputs task_data_fc.json
```
python3 generate_questions.py
```

Create a Hugging Face dataset from the task data. By default, this pushes mmbeliefs_mcq to your HF account.
```
python3 create_hfdataset.py
```

# Running Evaluation

## Setup Environment Variables

In ~/.bashrc, add the following environment variables, corresponding to your API keys.
```
HF_TOKEN
GOOGLE_API_KEY
ANTHROPIC_API_KEY
OPENAI_API_KEY
```

## Setup up lmms-eval

Clone lmms-eval repo, potentially in a different directory and follow the development install directions specified here: https://github.com/EvolvingLMMs-Lab/lmms-eval/

```
git clone https://github.com/EvolvingLMMs-Lab/lmms-eval
# ... follow the development install directions ...
```

Copy mmbeliefs_mcq.py runner file
```
cp lmms-eval-files/mmbeliefs_mcq.py lmms-eval/examples/models/
```

Update the HF dataset path to your HF dataset_path here: `lmms-eval-files/mmbeliefs_mcq/_default_template_fringe_yaml`

Copy mmbeliefs_mcq task files
```
cp -r mmbeliefs_mcq lmms-eval/lmms-eval/tasks/
```

## Run the Benchmark Task

Run evaluation
```
python3 lmms-eval/examples/models/mmbeliefs_mcq.py
```

# Important Notes

For Gemini 2.5 models, to pass images, use the gemini_api model rather than the openai compatible one.
Also, for Gemini 2.5 models, passing generation_config causes the model to return nothing.
