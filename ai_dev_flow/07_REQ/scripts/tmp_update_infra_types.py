
import os
import re

updates = {
    # Compute
    "REQ-06.02_cloud_functions.md": "Compute",
    "REQ-06.03_autoscaling_policies.md": "Compute",
    
    # Network
    "REQ-06.04_load_balancing.md": "Network",
    "REQ-06.05_ssl_termination.md": "Network",
    "REQ-06.06_cdn_integration.md": "Network",
    "REQ-06.22_vpc_network.md": "Network",
    "REQ-06.23_firewall_rules.md": "Network",
    "REQ-06.24_private_service_access.md": "Network",
    "REQ-06.25_cloud_nat.md": "Network",
    "REQ-06.26_dns_management.md": "Network",

    # Database
    "REQ-06.07_postgresql_primary.md": "Database",
    "REQ-06.08_postgresql_replica.md": "Database",
    "REQ-06.09_connection_pooling.md": "Database",
    "REQ-06.10_pgvector_extension.md": "Database",
    "REQ-06.11_apache_age_extension.md": "Database",
    "REQ-06.12_database_migrations.md": "Database",

    # Cache
    "REQ-06.13_redis_cache.md": "Cache",
    "REQ-06.14_cache_invalidation.md": "Cache",

    # Messaging
    "REQ-06.15_pubsub_topics.md": "Messaging",
    "REQ-06.16_pubsub_subscriptions.md": "Messaging",
    "REQ-06.17_dead_letter_queues.md": "Messaging",
    "REQ-06.18_message_retention.md": "Messaging",

    # Storage
    "REQ-06.19_cloud_storage.md": "Storage",
    "REQ-06.20_object_lifecycle.md": "Storage",
    "REQ-06.21_signed_urls.md": "Storage",

    # Deployment
    "REQ-06.31_iac_pipeline_stages.md": "Deployment_Automation",
    "REQ-06.32_container_registry.md": "Deployment_Automation",
    "REQ-06.33_terraform_state.md": "Deployment_Automation",
    "REQ-06.34_infrastructure_modules.md": "Deployment_Automation",
    "REQ-06.35_environment_promotion.md": "Deployment_Automation",
    "REQ-06.36_backup_automation.md": "Deployment_Automation",
    
    # Cost
    "REQ-06.39_cost_monitoring.md": "Cost",
    "REQ-06.40_budget_alerts.md": "Cost",
    
    # Security (Risk REQs) - Optional, but good to set if we have them in REQ-06 or elsewhere
    # REQ-06 doesn't seem to have explicit "Security group" files other than Firewall which is Network.
    
    # AI Infra
    "REQ-06.27_vertex_ai_integration.md": "Compute",
    "REQ-06.28_model_endpoints.md": "Compute",
}

base_dir = "/opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ/REQ-06_f6_infrastructure/"

def update_files():
    for filename, infra_type in updates.items():
        filepath = os.path.join(base_dir, filename)
        if not os.path.exists(filepath):
            print(f"Skipping {filename} (not found)")
            continue
            
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Replace Infrastructure Type
        # Pattern handles the table row
        pattern = r"\| \*\*Infrastructure Type\*\* \| .*? \|"
        replacement = f"| **Infrastructure Type** | {infra_type} |"
        
        new_content = re.sub(pattern, replacement, content)
        
        if new_content != content:
            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"Updated {filename} -> {infra_type}")
        else:
            print(f"No change for {filename} (already correct or pattern mismatch)")

if __name__ == "__main__":
    update_files()
