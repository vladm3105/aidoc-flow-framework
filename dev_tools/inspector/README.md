# Human Inspector (REPL)

Interactive debugging tool to pause Agent execution and modify state on the fly.

## Usage

1. Import the inspector in your agent code:
   ```python
   from dev_tools.inspector.inspector import inspect
   
   # ... agent logic ...
   payload = {"tool": "buy_stock", "args": {"symbol": "AAPL"}}
   
   # PAUSE HERE
   payload = inspect("Pre-Tool Execution", payload)
   
   # Resume with potentially modified payload
   execute_tool(payload)
   ```

2. Run your agent (MUST be interactive, not headless).

3. When the breakpoint is hit, you can:
   - `continue`: Proceed with original data.
   - `edit`: Paste new JSON to overwrite variables.
   - `abort`: Kill the process.
