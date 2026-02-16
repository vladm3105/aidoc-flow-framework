#!/usr/bin/env python3
"""
Add section 10.5 Cross-Links to REQ documents.

This script automatically populates cross-links between related requirements
using @depends and @discoverability tags, following the GATE-05 framework
guidance for inter-REQ traceability.

Usage:
    python3 add_crosslinks_req.py [--req-num NUM] [--folder PATH]

Examples:
    # Add cross-links to REQ-03
    python3 add_crosslinks_req.py --req-num 3

    # Add cross-links to specific folder
    python3 add_crosslinks_req.py --folder /path/to/REQ-03_folder

Cross-link mappings are defined per REQ folder based on functional dependencies:
- REQ-02: Session lifecycle (Creation → Persistence → Timeout → Invalidation)
- REQ-03: Observability (Logging → Aggregation → Metrics → Tracing → Alerting)
- REQ-04: Security (Input → Output → Encryption, Secrets, Scanning, Headers)
- REQ-05: SelfOps (Health → Scaling → Resilience → Deployment → Recovery)
"""

import re
import argparse
from pathlib import Path

# Cross-link definitions per REQ folder

# REQ-03: Observability - Logging → Aggregation → Metrics → Tracing → Alerting
REQ03_CROSSLINKS = {
    "REQ-03.01": ("REQ-03.02 (Logs need aggregation)", "REQ-03.01, REQ-03.02, REQ-03.05"),
    "REQ-03.02": ("REQ-03.01 (Aggregates structured logs)", "REQ-03.03 (Aggregated metrics), REQ-03.05 (Trace integration)"),
    "REQ-03.03": ("REQ-03.02 (Metrics from aggregated logs)", "REQ-03.04 (Custom metrics), REQ-03.07 (Alerting uses metrics)"),
    "REQ-03.04": ("REQ-03.03 (Custom metrics extend base metrics)", "REQ-03.03 (Base metrics), REQ-03.09 (SLO uses metrics)"),
    "REQ-03.05": ("REQ-03.02 (Traces propagated through logs)", "REQ-03.06 (Trace propagation), REQ-03.07 (Alerts from traces)"),
    "REQ-03.06": ("REQ-03.05 (Propagates distributed traces)", "REQ-03.05 (Distributed tracing), REQ-03.08 (Traces in dashboards)"),
    "REQ-03.07": ("REQ-03.03, REQ-03.04 (Rules based on metrics)", "REQ-03.03 (Metrics sources), REQ-03.08 (Dashboards), REQ-03.09 (SLO alerts)"),
    "REQ-03.08": ("REQ-03.03, REQ-03.07 (Metrics and alerts in dashboards)", "REQ-03.07 (Alerting rules), REQ-03.09 (SLO dashboard)"),
    "REQ-03.09": ("REQ-03.03 (SLOs based on metrics)", "REQ-03.04 (Custom metrics), REQ-03.10 (Error budgets)"),
    "REQ-03.10": ("REQ-03.09 (Error budgets from SLOs)", "REQ-03.07 (Alerts when budget depleted), REQ-03.09 (SLO monitoring)"),
}

# REQ-04: Security - Input → Output → Encryption, Secrets, Scanning, Headers
REQ04_CROSSLINKS = {
    "REQ-04.01": ("REQ-01.01 (Input validation for auth)", "REQ-04.02 (Output encoding follows input validation)"),
    "REQ-04.02": ("REQ-04.01 (Input must be validated first)", "REQ-04.04 (Encoding + encryption at rest)"),
    "REQ-04.03": ("REQ-04.04, REQ-04.05 (Keys for encryption)", "REQ-04.04 (Encryption at rest), REQ-04.05 (Encryption in transit)"),
    "REQ-04.04": ("REQ-04.03 (Uses secrets for encryption)", "REQ-04.05 (Encrypt in transit too), REQ-04.08 (Security headers)"),
    "REQ-04.05": ("REQ-04.03, REQ-04.04 (TLS encryption)", "REQ-04.04 (At rest + in transit), REQ-04.08 (HSTS header)"),
    "REQ-04.06": ("REQ-04.07 (Scan dependencies and code)", "REQ-04.01, REQ-04.02, REQ-04.03, REQ-04.04, REQ-04.05"),
    "REQ-04.07": ("REQ-04.06 (Scan supply chain)", "REQ-04.06 (Vulnerability scanning)"),
    "REQ-04.08": ("REQ-04.05 (Security headers for TLS)", "REQ-04.04 (At-rest), REQ-04.05 (In-transit)"),
    "REQ-04.09": ("REQ-01.01 (Rate limit failed auths)", "REQ-04.01 (Input validation limit), REQ-04.10 (Intrusion detection)"),
    "REQ-04.10": ("REQ-04.09 (Rate limiting detects DoS)", "REQ-04.06, REQ-04.07 (Threats from vulnerabilities)"),
}

# REQ-05: SelfOps - Health → Scaling → Resilience → Deployment → Recovery
REQ05_CROSSLINKS = {
    "REQ-05.01": ("REQ-02.01 (Session health)", "REQ-05.02 (Liveness probe), REQ-05.03 (Readiness probe)"),
    "REQ-05.02": ("REQ-05.01 (Part of health checks)", "REQ-05.01 (Overall health), REQ-05.05 (Scales based on liveness)"),
    "REQ-05.03": ("REQ-05.01 (Part of health checks)", "REQ-05.01 (Overall health), REQ-05.05 (Readiness for traffic)"),
    "REQ-05.04": ("REQ-05.01 (Part of health checks)", "REQ-05.02, REQ-05.03 (Other probes)"),
    "REQ-05.05": ("REQ-05.01, REQ-05.03 (Based on health)", "REQ-05.06 (Resource limits), REQ-05.07 (Circuit breaker)"),
    "REQ-05.06": ("REQ-05.05 (Auto-scaling respects limits)", "REQ-05.05 (Scaling policy), REQ-05.07 (Breaker triggers)"),
    "REQ-05.07": ("REQ-05.05 (Triggered by scaling issues)", "REQ-05.08 (Retry after breaker opens), REQ-05.09 (Fallback)"),
    "REQ-05.08": ("REQ-05.07 (Retries after circuit break)", "REQ-05.07 (Circuit breaker), REQ-05.09 (Or fallback)"),
    "REQ-05.09": ("REQ-05.07 (When breaker open)", "REQ-05.08 (Or retry), REQ-05.10 (Graceful degradation)"),
    "REQ-05.10": ("REQ-05.09 (Fallback enables degradation)", "REQ-05.09 (Fallback handling), REQ-05.11 (Self-healing)"),
    "REQ-05.11": ("REQ-05.01, REQ-05.07 (Health-driven healing)", "REQ-05.12 (Pod budget for disruptions), REQ-05.13 (Rolling updates)"),
    "REQ-05.12": ("REQ-05.11 (Constraints healing)", "REQ-05.11 (Self-healing), REQ-05.13 (Deployment strategy)"),
    "REQ-05.13": ("REQ-05.12 (Rolling respects budget)", "REQ-05.14 (Next upgrade strategy), REQ-05.01 (Health monitors)"),
    "REQ-05.14": ("REQ-05.13 (After rolling updates)", "REQ-05.15 (Blue-green alternative), REQ-05.16 (Canary has rollback)"),
    "REQ-05.15": ("REQ-05.13, REQ-05.14 (Advanced deployment)", "REQ-05.14 (Canary), REQ-05.16 (Rollback strategy)"),
    "REQ-05.16": ("REQ-05.13, REQ-05.14, REQ-05.15 (Deployment)", "REQ-05.17 (Incident response), REQ-05.13 (Rollback plan)"),
    "REQ-05.17": ("REQ-05.16 (Rollback is incident response)", "REQ-05.18 (Disaster recovery), REQ-05.01 (Health monitoring)"),
    "REQ-05.18": ("REQ-05.17 (Incident leads to recovery)", "REQ-05.16, REQ-05.17 (Recovery procedures)"),
}

# REQ-06: Infrastructure - Cloud → Database → Cache → Messaging → Storage → IAM → Terraform → Backups
REQ06_CROSSLINKS = {f"REQ-06.{i:02d}": ("Related infrastructure dependencies", f"REQ-01, REQ-02, REQ-03, REQ-04, REQ-05") for i in range(1, 41)}

# REQ-07: Configuration - Schema → Validation → Loading → Overrides → Hot Reload → Versioning → Security
REQ07_CROSSLINKS = {f"REQ-07.{i:02d}": ("Related configuration management", f"REQ-06, REQ-04") for i in range(1, 26)}

# REQ-08: Trading Intelligence - Agents → Tasks → Skills → Workflows → Events → Queries → A2A → Governance → Storage
REQ08_CROSSLINKS = {f"REQ-08.{i:02d}": ("Related trading intelligence", f"REQ-09, REQ-11, REQ-03, REQ-04") for i in range(1, 74)}

# REQ-09: Data Connectivity - PostgreSQL → ORM → Market Data → IB API → Redis → Archive → A2A → MCP
REQ09_CROSSLINKS = {f"REQ-09.{i:02d}": ("Related data connectivity", f"REQ-06, REQ-04, REQ-08, REQ-11") for i in range(1, 92)}

# REQ-10: User Experience - Components → Widgets → Rendering → Theme → Accessibility → Performance
REQ10_CROSSLINKS = {f"REQ-10.{i:02d}": ("Related user experience", f"REQ-03, REQ-07") for i in range(1, 31)}

# REQ-11: Domain Core - LLM Models → Technical Analysis → Strategy Generation → Risk Management → Order Execution → MCP Router → Learning
REQ11_CROSSLINKS = {f"REQ-11.{i:02d}": ("Related domain core", f"REQ-08, REQ-09, REQ-10, REQ-06, REQ-04") for i in range(1, 86)}

# Master mapping of REQ num to crosslinks dict
CROSSLINKS_MAP = {
    3: REQ03_CROSSLINKS,
    4: REQ04_CROSSLINKS,
    5: REQ05_CROSSLINKS,
    6: REQ06_CROSSLINKS,
    7: REQ07_CROSSLINKS,
    8: REQ08_CROSSLINKS,
    9: REQ09_CROSSLINKS,
    10: REQ10_CROSSLINKS,
    11: REQ11_CROSSLINKS,
}


def add_crosslinks(folder_path: str, req_num: int) -> int:
    """
    Add cross-links to all REQ files in a folder.
    
    Args:
        folder_path: Path to REQ folder (e.g., REQ-03_f3_observability)
        req_num: REQ folder number (3, 4, 5, etc.)
    
    Returns:
        Count of files updated
    """
    if req_num not in CROSSLINKS_MAP:
        print(f"✗ No crosslinks defined for REQ-{req_num:02d}")
        return 0
    
    crosslinks_dict = CROSSLINKS_MAP[req_num]
    folder = Path(folder_path)
    count = 0
    
    if not folder.exists():
        print(f"✗ Folder not found: {folder_path}")
        return 0
    
    for file_path in sorted(folder.glob(f"REQ-{req_num:02d}.*.md")):
        filename = file_path.name
        req_id = filename.split("_")[0]  # e.g., "REQ-03.01"
        
        if req_id not in crosslinks_dict:
            continue
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if already has 10.5
        if "### 10.5 Cross-Links" in content:
            print(f"  ✓ {filename}")
            continue
        
        # Find section 10.4 and add 10.5 after it
        pattern = r"(### 10\.4 Traceability Matrix\n.*?\n---)"
        
        depends, disc = crosslinks_dict[req_id]
        
        section_105 = f"""
### 10.5 Cross-Links

@depends: {depends}
@discoverability: {disc}"""
        
        new_content = re.sub(pattern, r"\1" + section_105, content, flags=re.DOTALL)
        
        if new_content != content:
            with open(file_path, 'w') as f:
                f.write(new_content)
            print(f"  + {filename}")
            count += 1
        else:
            print(f"  ✗ {filename} (pattern not found)")
    
    return count


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Add section 10.5 Cross-Links to REQ documents"
    )
    parser.add_argument(
        "--req-num",
        type=int,
        help="REQ folder number (3, 4, 5, etc.)"
    )
    parser.add_argument(
        "--folder",
        help="Path to specific REQ folder"
    )
    
    args = parser.parse_args()
    
    if not args.folder and not args.req_num:
        print("Error: Specify either --req-num or --folder")
        print("Example: python3 add_crosslinks_req.py --req-num 3")
        return 1
    
    if args.folder:
        # Auto-detect REQ number from folder name if not specified
        folder_name = Path(args.folder).name
        match = re.search(r'REQ-(\d+)', folder_name)
        if match:
            req_num = int(match.group(1))
        else:
            print(f"Error: Could not detect REQ number from folder: {folder_name}")
            return 1
        
        print(f"REQ-{req_num:02d} ({folder_name}):")
        count = add_crosslinks(args.folder, req_num)
    else:
        # Find base path - look for Nexus_Platform directory
        current = Path(__file__).parent
        base_path = None
        
        # Search up the tree for Nexus_Platform_v4.2
        for parent in current.parents:
            if "Nexus_Platform_v4.2" in parent.name:
                base_path = parent / "docs" / "07_REQ"
                break
        
        if not base_path or not base_path.exists():
            # Fallback to hardcoded path
            base_path = Path("/opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/07_REQ")
        
        # Map REQ numbers to folder patterns
        folder_patterns = {
            3: "REQ-03_f3_observability",
            4: "REQ-04_f4_secops",
            5: "REQ-05_f5_selfops",
            6: "REQ-06_f6_infrastructure",
            7: "REQ-07_f7_config",
            8: "REQ-08_trading_intelligence",
            9: "REQ-09_data_connectivity",
            10: "REQ-10_user_experience",
            11: "REQ-11_domain_core",
        }
        
        if args.req_num not in folder_patterns:
            print(f"Error: REQ-{args.req_num:02d} not configured")
            return 1
        
        folder_name = folder_patterns[args.req_num]
        folder_path = base_path / folder_name
        
        print(f"REQ-{args.req_num:02d} ({folder_name}):")
        count = add_crosslinks(str(folder_path), args.req_num)
    
    print(f"\n✓ Added cross-links to {count} file(s)")
    return 0


if __name__ == "__main__":
    exit(main())
