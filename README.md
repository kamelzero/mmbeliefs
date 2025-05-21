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
