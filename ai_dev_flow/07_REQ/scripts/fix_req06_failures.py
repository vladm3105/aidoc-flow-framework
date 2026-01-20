
import os
import re

dir_06 = "/opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ/REQ-06_f6_infrastructure/"

# Files to specific fixes
fixes = {
    # Category Fixes
    "REQ-06.31_iac_pipeline_stages.md": {"cat": "Infra", "infra": "Deployment_Automation", "add_deploy": True},
    "REQ-06.32_container_registry.md": {"cat": "Infra", "infra": "Deployment_Automation"},
    "REQ-06.33_terraform_state.md": {"cat": "Infra", "infra": "Deployment_Automation", "add_deploy": True},
    "REQ-06.34_infrastructure_modules.md": {"cat": "Infra", "infra": "Deployment_Automation", "add_deploy": True},
    "REQ-06.35_environment_promotion.md": {"cat": "Infra", "infra": "Deployment_Automation", "add_deploy": True},
    "REQ-06.36_backup_automation.md": {"cat": "Infra", "infra": "Deployment_Automation", "add_deploy": True},
    "REQ-06.39_cost_monitoring.md": {"cat": "Infra"},
    "REQ-06.37_point_in_time_recovery.md": {"cat": "Reliability"}, # Was Disaster Recovery
    "REQ-06.01_cloud_run_deployment.md":  {"cat": "Infra"}, # Make sure
    
    # Check "skipped" files from before just in case
    "REQ-06.15_pubsub_topics.md": {"infra": "Messaging"},
    "REQ-06.16_pubsub_subscriptions.md": {"infra": "Messaging"},
    "REQ-06.17_dead_letter_queues.md": {"infra": "Messaging"},
    "REQ-06.18_message_retention.md": {"infra": "Messaging"},
}

def fix_files():
    for filename, data in fixes.items():
        filepath = os.path.join(dir_06, filename)
        if not os.path.exists(filepath):
            print(f"Skipping {filename} (not found in {dir_06})")
            continue
            
        with open(filepath, 'r') as f:
            content = f.read()

        new_content = content
        
        # fix category if specified
        if "cat" in data:
            # Replace whatever Category is there with new one
            # Using specific pattern to catch "Infrastructure", "FinOps" etc
            new_content = re.sub(r"\| \*\*Category\*\* \| .*? \|", f"| **Category** | {data['cat']} |", new_content)

        # fix infra if specified (handling skipped ones)
        if "infra" in data:
             new_content = re.sub(r"\| \*\*Infrastructure Type\*\* \| .*? \|", f"| **Infrastructure Type** | {data['infra']} |", new_content)

        # add @deployment tag if needed
        if data.get("add_deploy", False):
             if not re.search(r"@deployment:", new_content):
                 # Find Traceability and append
                 trace_match = re.search(r"(##\s*10\.\s*Traceability.*?)(\n##\s|\Z)", new_content, re.DOTALL)
                 if trace_match:
                     section = trace_match.group(1)
                     new_section = section.rstrip() + "\n@deployment: scripts/\n"
                     new_content = new_content.replace(section, new_section)
        
        if new_content != content:
            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"Fixed {filename}")
        else:
            print(f"No changes for {filename}")

if __name__ == "__main__":
    fix_files()
