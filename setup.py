from pathlib import Path

from setuptools import find_packages, setup

# Load packages from requirements.txt
BASE_DIR = Path(__file__).parent
with open(Path(BASE_DIR, "requirements.txt")) as file:
    required_packages = [ln.strip() for ln in file.readlines()]

# Define our package
setup(
    name="llm_utils",
    version=0.1,
    description="General tools for LLM-based apps",
    author="Ryan Melvin",
    author_email="rmelvin@uabmc.edu",
    url="https://github.com/UABPeriopAI/llm_utils.git",
    python_requires=">=3.10",
    packages=find_packages(), # only look in directores with __init__.py
    install_requires=[required_packages],
)
