
import os
import re

# Base Directories
dir_06 = "/opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ/REQ-06_f6_infrastructure/"
dir_05 = "/opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ/REQ-05_f5_selfops/"
dir_04 = "/opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ/REQ-04_f4_secops/"

# Files that require IaC tags (same lists as before, excluding Cost/None)
files_to_update = {
    # REQ-06 (Infra)
    "REQ-06.01_cloud_run_deployment.md": dir_06,
    "REQ-06.02_cloud_functions.md": dir_06,
    "REQ-06.03_autoscaling_policies.md": dir_06,
    "REQ-06.04_load_balancing.md": dir_06,
    "REQ-06.05_ssl_termination.md": dir_06,
    "REQ-06.06_cdn_integration.md": dir_06,
    "REQ-06.22_vpc_network.md": dir_06,
    "REQ-06.23_firewall_rules.md": dir_06,
    "REQ-06.24_private_service_access.md": dir_06,
    "REQ-06.25_cloud_nat.md": dir_06,
    "REQ-06.26_dns_management.md": dir_06,
    "REQ-06.07_postgresql_primary.md": dir_06,
    "REQ-06.08_postgresql_replica.md": dir_06,
    "REQ-06.09_connection_pooling.md": dir_06,
    "REQ-06.10_pgvector_extension.md": dir_06,
    "REQ-06.11_apache_age_extension.md": dir_06,
    "REQ-06.12_database_migrations.md": dir_06,
    "REQ-06.13_redis_cache.md": dir_06,
    "REQ-06.14_cache_invalidation.md": dir_06,
    "REQ-06.15_pubsub_topics.md": dir_06,
    "REQ-06.16_pubsub_subscriptions.md": dir_06,
    "REQ-06.17_dead_letter_queues.md": dir_06,
    "REQ-06.18_message_retention.md": dir_06,
    "REQ-06.19_cloud_storage.md": dir_06,
    "REQ-06.20_object_lifecycle.md": dir_06,
    "REQ-06.21_signed_urls.md": dir_06,
    "REQ-06.31_iac_pipeline_stages.md": dir_06, # Deployment
    "REQ-06.32_container_registry.md": dir_06,
    "REQ-06.33_terraform_state.md": dir_06,
    "REQ-06.34_infrastructure_modules.md": dir_06,
    "REQ-06.35_environment_promotion.md": dir_06,
    "REQ-06.36_backup_automation.md": dir_06,
    "REQ-06.27_vertex_ai_integration.md": dir_06,
    "REQ-06.28_model_endpoints.md": dir_06,

    # REQ-05 (SelfOps - Deployment/Compute/Scalability)
    "REQ-05.05_auto_scaling.md": dir_05,
    "REQ-05.06_resource_limits.md": dir_05,
    "REQ-05.13_rolling_updates.md": dir_05,
    "REQ-05.14_canary_deployment.md": dir_05,
    "REQ-05.15_blue_green_deployment.md": dir_05,
    "REQ-05.16_rollback_automation.md": dir_05,
    "REQ-05.18_disaster_recovery.md": dir_05,
    "REQ-05.12_pod_disruption_budget.md": dir_05,

    # REQ-04 (SecOps)
    "REQ-04.03_secrets_management.md": dir_04,
    "REQ-04.04_encryption_at_rest.md": dir_04,
    "REQ-04.05_encryption_in_transit.md": dir_04,
    "REQ-04.06_vulnerability_scanning.md": dir_04,
    "REQ-04.08_security_headers.md": dir_04,
    "REQ-04.10_intrusion_detection.md": dir_04,
}

def update_files():
    for filename, directory in files_to_update.items():
        filepath = os.path.join(directory, filename)
        if not os.path.exists(filepath):
            # checking common alternative location just in case
            continue
            
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Check if already has tags (case insensitive)
        if re.search(r"@iac:|@ansible:", content, re.IGNORECASE):
            print(f"Skipping {filename} (already has tags)")
            continue

        # Find Traceability section block
        # Matches from '## 10. Traceability' until next header '## ' or End of String
        trace_match = re.search(r"(##\s*10\.\s*Traceability.*?)(\n##\s|\Z)", content, re.DOTALL)
        
        if trace_match:
            section_content = trace_match.group(1)
            # Find the ### Traceability Tags or equivalent part to append to
            # If not found, just append to section content
            
            new_section_content = section_content.rstrip() + "\n@iac: terraform/\n"
            
            new_content = content.replace(section_content, new_section_content)
            
            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"Updated {filename} with @iac tag")
        else:
            print(f"Warning: Could not find Traceability section in {filename}")

if __name__ == "__main__":
    update_files()
