# Agent Evaluator (Promptfoo)

Automated quality assurance for your generic agents using "LLM-as-a-Judge".

## Setup

```bash
npm install -g promptfoo
```

## Usage

1.  Edit `agent_wrapper.py` to call your actual agent.
2.  Edit `promptfooconfig.yaml` to define test cases.
3.  Run evaluation:

```bash
npx promptfoo eval
```

4.  View results:

```bash
npx promptfoo view
```
