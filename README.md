# OpsAgentAI

A local-first autonomous AI agent that plans, uses tools, and answers with real operational context without requiring an external API key.

## What this version does

This project uses a local model via Ollama instead of OpenAI. That means:

- no OpenAI API key required
- works on your own machine
- good for local testing and self-hosted use
- still supports reasoning, planning, and tool usage

## Prerequisites

1. Python 3.10+
2. Ollama installed locally
3. A local model pulled into Ollama

## Install Ollama

Linux/macOS:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Then pull a model:

```bash
ollama pull llama3.2
```

## Install project dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Example task

```text
Inspect this project and tell me what it looks like, what files are present, and what the next best action should be.
```

## Notes

- This project uses the local Ollama endpoint at `http://localhost:11434`
- The agent can call local tools such as file exploration and shell commands
- It is designed to be extended with more operations and integrations

## Why not Vercel for this exact setup?

Vercel is a serverless deployment platform. A local model running on your machine is not usually available from Vercel unless you deploy a separate self-hosted backend. For a truly local/self-hosted AI, this repo is meant to run on your machine or on a private server.
