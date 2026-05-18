# Log Analyzer

A CLI tool to parse agent logs and generate a "Battle Report" of costs and errors.

## Usage

```bash
python analyzer.py /path/to/logfile.log
```

## Options
- `--format`: `text` (default) or `jsonl`. 
- `--error-keywords`: Custom keywords to search for (default: "Error,Exception,Fail").

## Output
Displays a rich table with:
- Total Lines
- Total Tokens (scraped via regex `Tokens Used: X`)
- Estimated Cost
- Error Counts by Keyword
