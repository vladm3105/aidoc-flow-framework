
import os
import re

dir_10 = "/opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ/REQ-10_user_experience/"

# Value-based mappings (Old -> New)
mappings = {
    "UI Accessibility": "Compliance",
    "UI Architecture": "Logic",
    "UI Configuration": "Config",
    "UI Customization": "UI",
    "UI Data Layer": "Logic",
    "UI Feedback": "UI",
    "UI Infrastructure": "Logic",
    "UI Layout": "UI",
    "UI Performance": "Performance",
    "UI Reliability": "Reliability",
    "UI Rendering": "UI",
    "UI Theming": "UI",
    "User Settings": "Config",
}

def fix_files():
    if not os.path.exists(dir_10):
        print(f"Directory not found: {dir_10}")
        return

    for filename in os.listdir(dir_10):
        if not filename.endswith(".md"): continue
        
        filepath = os.path.join(dir_10, filename)
        with open(filepath, 'r') as f:
            content = f.read()
            
        new_content = content
        for old_cat, new_cat in mappings.items():
            # Regex to match exact Category cell content
            pattern = re.escape(f"| **Category** | {old_cat} |")
            replacement = f"| **Category** | {new_cat} |"
            new_content = re.sub(pattern, replacement, new_content)
            
        if new_content != content:
            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"Fixed {filename}")

if __name__ == "__main__":
    fix_files()
