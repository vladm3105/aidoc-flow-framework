# `.aidoc/` Blueprint: gVisor (`runsc`) Sandbox & Infisical Execution Profile

## Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-10-10 |
| Author | Framework Maintainer |
| Framework Version | 0.91.3 |
| Authority | [RECOMMENDED_PLATFORM_STACK.md](../RECOMMENDED_PLATFORM_STACK.md) & [WORKTREE_FLOW.md](../WORKTREE_FLOW.md) |

Operational blueprint defining the security, runtime isolation, and secret injection profile
for running autonomous coding agents and untrusted dynamic tasks under **gVisor (`runsc`)** and **Infisical**.

---

## 1. Security Invariants

1. **User-Space Kernel Virtualization:**
   Dynamic execution containers MUST run under the **gVisor (`runsc`)** OCI runtime. Direct host kernel execution (`runc`) is forbidden for autonomous agent runners.
2. **Strict Network Isolation:**
   Agent coding containers run with `--network=none` to prevent data exfiltration, lateral network attacks, and unauthorized external connections.
3. **Restricted Model Egress via UNIX Socket:**
   To access LLMs, the host UNIX domain socket `/var/run/litellm.sock` is bind-mounted read-write (`:rw`) into the container. The agent communicates with LiteLLM over HTTP via UNIX socket, bypassing TCP network stacks completely.
4. **Least-Privilege Non-Root Execution:**
   Containers execute as `USER 1000:1000` with all capabilities dropped (`--cap-drop=ALL`) and read-only root filesystems (`--read-only`).
5. **In-Memory Secret Provisioning:**
   Secrets MUST NOT be written to `.env` files or baked into images. Containers execute `infisical run -- <command>` to pull machine credentials directly into process RAM at launch.

---

## 2. Host Daemon Configuration (`/etc/docker/daemon.json`)

```json
{
  "default-runtime": "runc",
  "runtimes": {
    "runsc": {
      "path": "/usr/bin/runsc",
      "runtimeArgs": [
        "--platform=systrap",
        "--strace=false"
      ]
    }
  }
}
```

---

## 3. Docker Compose Agent Runner Template

```yaml
version: "3.8"

services:
  agent-runner:
    image: ghcr.io/ecosystem/agent-runner:latest
    runtime: runsc
    network_mode: none
    user: "1000:1000"
    read_only: true
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    
    # In-memory temporary scratch spaces
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=512m
      - /home/agent/.cache:rw,noexec,nosuid,size=1g
    
    volumes:
      # Isolated git worktree directory
      - /mnt/worktrees/task-1234:/workspace:rw
      
      # LiteLLM UNIX domain socket for LLM proxy calls
      - /var/run/litellm.sock:/var/run/litellm.sock:rw
      
      # Infisical machine identity configuration
      - /etc/infisical/auth.json:/etc/infisical/auth.json:ro
    
    environment:
      - WORKSPACE_DIR=/workspace
      - OPENAI_BASE_URL=http://localhost/v1
      - OPENAI_API_KEY=unused-proxy-auth
      - LITELLM_SOCKET=/var/run/litellm.sock
    
    # In-memory secret injection entrypoint
    entrypoint: ["infisical", "run", "--env=prod", "--path=/agent-worker", "--"]
    command: ["python3", "-m", "worker.run_task"]
```

---

## 4. Worktree CLI Execution Command Pattern

When dispatching an ephemeral task CLI runner from Temporal activities:

```bash
docker run --rm \
  --runtime=runsc \
  --network=none \
  --user=1000:1000 \
  --cap-drop=ALL \
  --read-only \
  --tmpfs /tmp:rw,size=256m \
  -v "/mnt/worktrees/${TASK_SLUG}:/workspace:rw" \
  -v "/var/run/litellm.sock:/var/run/litellm.sock:rw" \
  -e "OPENAI_BASE_URL=http://localhost/v1" \
  agent-runner:latest \
  infisical run -- python3 -m worker.execute_plan --worktree=/workspace
```
