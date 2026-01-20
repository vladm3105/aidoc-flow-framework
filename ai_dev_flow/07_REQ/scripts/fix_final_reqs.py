
import os
import re

dir_10 = "/opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ/REQ-10_f10_frontend/"
dir_05 = "/opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ/REQ-05_f5_selfops/"

updates = {
    # Fix REQ-05 Deployment Tags
    "REQ-05.13_rolling_updates.md": {"dir": dir_05, "add_deploy": True},
    "REQ-05.14_canary_deployment.md": {"dir": dir_05, "add_deploy": True},
    "REQ-05.15_blue_green_deployment.md": {"dir": dir_05, "add_deploy": True},
    "REQ-05.16_rollback_automation.md": {"dir": dir_05, "add_deploy": True},
    "REQ-05.18_disaster_recovery.md": {"dir": dir_05, "add_deploy": True},
    
    # Fix REQ-10 Categories (User Interface -> UI, UX -> UI, etc.)
    # Assuming batch fix for common errors seen in logs or anticipated
}

# Dynamic scanner for REQ-10 to catch "User Interface" etc.
def fix_files():
    # 1. Apply explicit updates (REQ-05)
    for filename, data in updates.items():
        filepath = os.path.join(data["dir"], filename)
        if not os.path.exists(filepath): continue
        
        with open(filepath, 'r') as f: content = f.read()
        new_content = content
        
        if data.get("add_deploy", False):
             if not re.search(r"@deployment:", new_content):
                 trace_match = re.search(r"(##\s*10\.\s*Traceability.*?)(\n##\s|\Z)", new_content, re.DOTALL)
                 if trace_match:
                     section = trace_match.group(1)
                     new_section = section.rstrip() + "\n@deployment: scripts/\n"
                     new_content = new_content.replace(section, new_section)
        
        if new_content != content:
            with open(filepath, 'w') as f: f.write(new_content)
            print(f"Fixed {filename}")

    # 2. Scan REQ-10 for Invalid Categories
    if os.path.exists(dir_10):
        for filename in os.listdir(dir_10):
            if not filename.endswith(".md"): continue
            filepath = os.path.join(dir_10, filename)
            with open(filepath, 'r') as f: content = f.read()
            
            new_content = content
            # Map "User Interface" -> "UI"
            new_content = re.sub(r"\| \*\*Category\*\* \| User Interface \|", "| **Category** | UI |", new_content)
            # Map "UI Accessibility" -> "UI" (or Compliance, but UI fits broadly)
            new_content = re.sub(r"\| \*\*Category\*\* \| UI Accessibility \|", "| **Category** | UI |", new_content)
            # Map "Frontend" -> "UI"
            new_content = re.sub(r"\| \*\*Category\*\* \| Frontend \|", "| **Category** | UI |", new_content)
            
            if new_content != content:
                with open(filepath, 'w') as f: f.write(new_content)
                print(f"Fixed Category in {filename}")

if __name__ == "__main__":
    fix_files()
