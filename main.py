import json
import os

import requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

SYSTEM_PROMPT = """
You are a practical operations AI agent.

You must act as a helper that can:
- think through tasks
- choose the best tool
- do real work on files and commands
- answer with operational, evidence-based results

Return STRICT JSON only:
{
  "type": "tool_call" or "final",
  "tool": "name_of_tool_or_null",
  "args": {...},
  "answer": "final answer if type=final"
}

Rules:
- Use tool_call when more information is needed.
- Use final when enough evidence exists to respond.
- Only use tools from this list: run_shell, read_file, list_dir, search_files
- Do not invent results.
- If final, include concrete actions and validation steps.
"""


def ask_llm(system_prompt, user_prompt):
    payload = {
        "model": MODEL,
        "prompt": f"{system_prompt}\n\n{user_prompt}",
        "stream": False,
        "options": {
            "temperature": 0.2,
        },
    }

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            f"Could not reach Ollama at {OLLAMA_URL}. Start Ollama and pull a model first. Details: {exc}"
        ) from exc


class Agent:
    def __init__(self, tools, working_dir="."):
        self.tools = tools
        self.working_dir = working_dir
        self.memory = []

    def run(self, task, max_steps=8):
        step = 0
        while step < max_steps:
            context = "\n".join(self.memory[-8:]) if self.memory else "No previous tool results."
            user_prompt = f"""
Task:
{task}

Working directory:
{self.working_dir}

Memory / prior observations:
{context}

Decide the next action.
Return JSON only.
"""
            raw = ask_llm(SYSTEM_PROMPT, user_prompt)
            print("LLM decision:", raw)

            try:
                action = json.loads(raw)
            except json.JSONDecodeError:
                return raw

            if action.get("type") == "final":
                return action.get("answer", raw)

            tool_name = action.get("tool")
            args = action.get("args", {})

            if tool_name not in self.tools:
                return f"Tool not allowed: {tool_name}"

            if tool_name in ("read_file", "list_dir", "search_files"):
                if "path" not in args and "root" not in args:
                    args["path"] = self.working_dir
                if "path" in args and not os.path.isabs(args["path"]):
                    args["path"] = os.path.join(self.working_dir, args["path"])
                if "root" in args and not os.path.isabs(args["root"]):
                    args["root"] = os.path.join(self.working_dir, args["root"])

            result = self.tools[tool_name](**args)
            self.memory.append(
                f"Step {step}: tool={tool_name}, args={json.dumps(args, default=str)}, result={str(result)[:1500]}"
            )
            step += 1

        return "Task ended without reaching a final answer within the step limit."
