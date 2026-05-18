import os
import json
import logging
from typing import List
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="Context Viewer")

# Setup Paths
BASE_DIR = Path(__file__).resolve().parent
CONTEXT_DIR = BASE_DIR / "debug_contexts"
CONTEXT_DIR.mkdir(exist_ok=True) # Ensure dir exists

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/", response_class=HTMLResponse)
async def list_contexts(request: Request):
    """List all saved context JSON files"""
    files = sorted(CONTEXT_DIR.glob("*.json"), key=os.path.getmtime, reverse=True)
    file_list = [{"name": f.name, "size": f.stat().st_size} for f in files]
    return templates.TemplateResponse("index.html", {"request": request, "files": file_list})

@app.get("/view/{filename}", response_class=HTMLResponse)
async def view_context(request: Request, filename: str):
    """View a specific context file"""
    file_path = CONTEXT_DIR / filename
    if not file_path.exists():
        return HTMLResponse(content="File not found", status_code=404)
    
    with open(file_path, "r") as f:
        try:
            data = json.load(f)
            formatted_json = json.dumps(data, indent=2)
        except Exception:
            formatted_json = "Error reading JSON"
            
    return templates.TemplateResponse("viewer.html", {"request": request, "filename": filename, "content": formatted_json})

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=9004)
    args = parser.parse_args()
    uvicorn.run(app, host="0.0.0.0", port=args.port)
