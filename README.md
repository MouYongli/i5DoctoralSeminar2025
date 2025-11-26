# Tutorial: Large Language Models and AI Agent Systems

This repository is a collection of materials for the tutorial on the RWTH DBIS and Fraunhofer FIT Doctoral Seminar 2025 on the topic of Large Language Models and AI Agent Systems. This tutorial is designed to provide a comprehensive introduction to large language models (LLMs) and AI agent systems, including the fundamental concepts, architectures, and applications of LLMs and AI agents.

## Overview

- **Duration**: 90 minutes
- **Speaker**: Yongli Mou (RWTH DBIS)
- **Target Audience**: PhD students/researchers
- **Date**: 2025-10-23
- **Location**: Aachen, Germany
- **Main Content**:
  - Part 1: Introduction to Large Language Models
  - Part 2: Introduction to AI Agent Systems
  - Part 3: Advanced Topics
  - Part 4: Summary and Discussion

## Structure

The repository is organized into the following directories:
- `README.md`: Contains the README file for the tutorial.
- `slides`: Contains the slides for the tutorial.
- `code`: Contains the code examples for the tutorial.
    - `pyproject.toml`: Contains the pyproject.toml file for the tutorial.
    - `src`: Contains the source code for the tutorial.
    - `notebooks`: Contains the notebooks for the tutorial.
    - `tests`: Contains the tests for the tutorial.
- `data`: Contains the data for the tutorial.
- `docs`: Contains the documentation for the tutorial.

## Quick Start

### Slides
The slides are written in LaTeX and can be compiled using the `compile.sh` script.
1. Using bash scripts

```bash
cd slides
# Setup the LaTeX environment
./scripts/setup.sh
# Compile the slides
./scripts/compile.sh main.tex
# Clean the LaTeX environment
./scripts/clean.sh
```

2. Using `Makefile`

```bash
cd slides
# Setup the LaTeX environment
make setup
# Compile the slides
make all
# Clean the build directory
make clean
```

### Code

#### FastMCP Example

#### LangChain Example

#### i5 Agents Example

The code examples are written in Python and can be run using the `uv` command.

1. Setup the Python environment
```bash
cd code/i5agents

cd docker

# Activate the virtual environment
uv venv --python 3.12
# Activate the virtual environment
source .venv/bin/activate
# Install the dependencies
uv sync
```

2. Run the command to run the agent
```bash
# Run the agent (script mode: `pyproject.toml` defines the entry point)
uv run i5_agent.run --config config/config.yaml --goal "What is the capital of France?"
# Run the agent with the python interpreter (module mode: `__main__.py` defines the entry point)
uv run python -m i5_agent.agent.run --config config/config.yaml --goal "What is the capital of France?"
```

