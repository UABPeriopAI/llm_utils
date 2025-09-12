#!/bin/sh
PROJECT_ROOT="/workspaces/llm_utils"   
VENV_PATH="$PROJECT_ROOT/.venv"         # Note: env kept in the repo folder

# Install uv globally first
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create the virtual environment with uv
uv venv "$VENV_PATH" --clear

# Install uv **inside** that newly created venv to be safe
"$VENV_PATH/bin/python" -m pip install uv

# Use the venv's uv
export PATH="$VENV_PATH/bin:$PATH"

uv sync --locked --all-extras --dev

make venv

# Ensure every new shell auto-activates the venv
echo 'source $PROJECT_ROOT/.venv/bin/activate' >> /home/vscode/.bashrc
echo 'source $PROJECT_ROOT/.venv/bin/activate' >> /home/vscode/.zshrc

echo 'export PYTHONPATH="$PROJECT_ROOT/llm_utils:${PYTHONPATH}"' >> ~/.profile

source .venv/bin/activate