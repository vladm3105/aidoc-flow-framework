
import os
import re

# Base Directories
dir_04 = "/opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ/REQ-04_f4_secops/"
dir_05 = "/opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ/REQ-05_f5_selfops/"

updates = {
    # REQ-04: Category=Security, InfraType=Security
    "REQ-04.03_secrets_management.md": {"dir": dir_04, "cat": "Security", "infra": "Security"},
    "REQ-04.04_encryption_at_rest.md": {"dir": dir_04, "cat": "Security", "infra": "Security"},
    "REQ-04.05_encryption_in_transit.md": {"dir": dir_04, "cat": "Security", "infra": "Security"},
    "REQ-04.06_vulnerability_scanning.md": {"dir": dir_04, "cat": "Security", "infra": "Security"},
    "REQ-04.08_security_headers.md": {"dir": dir_04, "cat": "Security", "infra": "Security"},
    "REQ-04.10_intrusion_detection.md": {"dir": dir_04, "cat": "Security", "infra": "Security"},
    
    # REQ-05: Category=Reliability/Infra, InfraType=Deployment_Automation/Compute
    "REQ-05.05_auto_scaling.md": {"dir": dir_05, "cat": "Scalability", "infra": "Compute"},
    "REQ-05.06_resource_limits.md": {"dir": dir_05, "cat": "Scalability", "infra": "Compute"},
    "REQ-05.13_rolling_updates.md": {"dir": dir_05, "cat": "Reliability", "infra": "Deployment_Automation"},
    "REQ-05.14_canary_deployment.md": {"dir": dir_05, "cat": "Reliability", "infra": "Deployment_Automation"},
    "REQ-05.15_blue_green_deployment.md": {"dir": dir_05, "cat": "Reliability", "infra": "Deployment_Automation"},
    "REQ-05.16_rollback_automation.md": {"dir": dir_05, "cat": "Reliability", "infra": "Deployment_Automation"},
    "REQ-05.18_disaster_recovery.md": {"dir": dir_05, "cat": "Reliability", "infra": "Deployment_Automation"},
    "REQ-05.12_pod_disruption_budget.md": {"dir": dir_05, "cat": "Reliability", "infra": "Compute"}, # or Deployment
}

def update_files():
    for filename, data in updates.items():
        filepath = os.path.join(data["dir"], filename)
        if not os.path.exists(filepath):
            print(f"Skipping {filename} (not found)")
            continue
            
        with open(filepath, 'r') as f:
            content = f.read()
            
        new_content = content
        
        # Replace Category
        cat_pattern = r"\| \*\*Category\*\* \| .*? \|"
        cat_replacement = f"| **Category** | {data['cat']} |"
        new_content = re.sub(cat_pattern, cat_replacement, new_content)

        # Replace Infrastructure Type
        infra_pattern = r"\| \*\*Infrastructure Type\*\* \| .*? \|"
        infra_replacement = f"| **Infrastructure Type** | {data['infra']} |"
        new_content = re.sub(infra_pattern, infra_replacement, new_content)
        
        if new_content != content:
            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"Updated {filename} -> Cat: {data['cat']}, Infra: {data['infra']}")
        else:
            print(f"No change for {filename}")

if __name__ == "__main__":
    update_files()
