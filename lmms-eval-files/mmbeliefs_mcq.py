#!/usr/bin/env python3

"""
# Run all models (default behavior)
python3 mmbeliefs_mcq.py

# Run specific models
python3 mmbeliefs_mcq.py --models mistral claude

# Run a single model
python3 mmbeliefs_mcq.py --models gpt4
"""

import os
import argparse
import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Define model configurations
MODEL_CONFIGS = {
    'mistral': {
        'api_base': "https://router.huggingface.co/nebius/v1",
        'model_version': "mistralai/Mistral-Small-3.1-24B-Instruct-2503",
        'api_key_env': 'HF_TOKEN',
        'output_dir': "mistral-small-3.1-24b-instruct-2503_api"
    },
    'gemini': {
        'api_base': "https://generativelanguage.googleapis.com/v1beta/openai/",
        'model_version': "gemini-2.0-flash",
        'api_key_env': 'GOOGLE_API_KEY',
        'output_dir': "gemini-2.0-flash_api"
    },
    'claude': {
        'api_base': "https://api.anthropic.com/v1/",
        'model_version': "claude-3-7-sonnet-20250219",
        'api_key_env': 'ANTHROPIC_API_KEY',
        'output_dir': "claude-3-7-sonnet-20250219_api"
    },
    'llama': {
        'api_base': "https://router.huggingface.co/together/v1",
        'model_version': "meta-llama/Llama-4-Scout-17B-16E-Instruct",
        'api_key_env': 'HF_TOKEN',
        'output_dir': "llama4_scout_17b_16e_instruct_api"
    },
    'qwen': {
        'api_base': "https://router.huggingface.co/hyperbolic/v1",
        'model_version': "Qwen/Qwen2.5-VL-7B-Instruct",
        'api_key_env': 'HF_TOKEN',
        'output_dir': "qwen2_5_vl_7b_api"
    },
    'gpt4': {
        'api_base': "https://api.openai.com/v1",
        'model_version': "gpt-4o-2024-11-20",
        'api_key_env': 'OPENAI_API_KEY',
        'output_dir': "gpt-4o-2024-11-20",
        'extra_args': 'azure_openai=False'
    }
}

def check_required_env_vars():
    """Check if required environment variables are set."""
    required_vars = {'HF_TOKEN', 'OPENAI_API_KEY'}
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

def run_model_evaluation(model_name: str, config: Dict):
    """Run evaluation for a specific model."""
    logging.info(f"Starting evaluation for {model_name}")
    
    # Set environment variables for this run
    os.environ['OPENAI_API_KEY'] = os.getenv(config['api_key_env'])
    os.environ['OPENAI_API_BASE'] = config['api_base']
    
    # Construct command
    extra_args = f",{config.get('extra_args', '')}" if config.get('extra_args') else ''
    cmd = (
        f"python3 -m lmms_eval "
        f"--model openai_compatible "
        f"--model_args model_version={config['model_version']}{extra_args} "
        f"--tasks mmbeliefs_mcq "
        f"--batch_size 1 "
        f"--log_samples "
        f"--output_path ./mmbeliefs_mcq_results/{config['output_dir']}"
    )
    
    logging.info(f"Executing command: {cmd}")
    exit_code = os.system(cmd)
    
    if exit_code == 0:
        logging.info(f"Successfully completed evaluation for {model_name}")
    else:
        logging.error(f"Failed to complete evaluation for {model_name}")

def main():
    parser = argparse.ArgumentParser(description='Run model evaluations on mmbeliefs_mcq dataset')
    parser.add_argument('--models', nargs='+', choices=list(MODEL_CONFIGS.keys()) + ['all'],
                      default=['all'], help='List of models to evaluate')
    args = parser.parse_args()
    
    # Check environment variables
    check_required_env_vars()
    
    # Determine which models to run
    models_to_run = list(MODEL_CONFIGS.keys()) if 'all' in args.models else args.models
    
    logging.info(f"Starting evaluation for models: {', '.join(models_to_run)}")
    
    # Run evaluations
    for model_name in models_to_run:
        run_model_evaluation(model_name, MODEL_CONFIGS[model_name])
    
    logging.info("All evaluations completed")

if __name__ == "__main__":
    main()