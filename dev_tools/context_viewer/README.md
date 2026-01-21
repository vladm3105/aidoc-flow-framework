# Context Viewer

A Web UI to inspect the "Context" (Prompt History) of your Agents.

## Usage

1. Save your agent's context (list of messages) as a JSON file in `debug_contexts/`.
   ```python
   # Example in your agent code
   import json
   with open("dev_tools/context_viewer/debug_contexts/my_agent_run.json", "w") as f:
       json.dump(agent.messages, f)
   ```

2. Run the Viewer:
   ```bash
   python viewer.py
   ```

3. Open `http://localhost:9004` in your browser.
