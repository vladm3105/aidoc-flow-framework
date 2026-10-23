# `.aidoc/` Blueprint: gVisor (`runsc`) Sandbox & Two-Tier Secrets Execution Profile

## Document Control

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-10-19 |
| Author | Framework Maintainer |
| Framework Version | 0.96.12 |
| Authority | [RECOMMENDED_PLATFORM_STACK.md](../RECOMMENDED_PLATFORM_STACK.md) & [WORKTREE_FLOW.md](../WORKTREE_FLOW.md) |

Operational blueprint defining the security, runtime isolation, and secret injection profile
for running autonomous coding agents and untrusted dynamic tasks under **gVisor (`runsc`)** and **Two-Tier Secrets (OCI Vault + OpenBao)**.

---

## 1. Security Invariants

1. **User-Space Kernel Virtualization:**
   Dynamic execution containers MUST run under the **gVisor (`runsc`)** OCI runtime in production. Direct host kernel execution (`runc`) is forbidden for untrusted autonomous agent runners. *(Escape valve: local developer environments on macOS/Windows and unprivileged CI runners lacking nested virtualization MAY fall back to `runc` provided that `--cap-drop=ALL`, `--security-opt=no-new-privileges:true`, and `--read-only` remain strictly enforced).*
2. **Strict Network Isolation:**
   Agent coding containers run with `--network=none` to prevent data exfiltration, lateral network attacks, and unauthorized external connections.
3. **Restricted Model Egress via UNIX Socket:**
   To access LLMs, the host UNIX domain socket `/var/run/litellm.sock` is bind-mounted read-write (`:rw`) into the container. The agent communicates with LiteLLM over HTTP via UNIX socket (e.g. `http+unix://%2Fvar%2Frun%2Flitellm.sock/v1`), bypassing TCP network stacks completely.
4. **Least-Privilege Non-Root Execution:**
   Containers execute as non-root user (`USER 1000:1000` or host `${UID}:${GID}`) with all capabilities dropped (`--cap-drop=ALL`) and read-only root filesystems (`--read-only`).
5. **In-Memory Secret Provisioning:**
   Secrets MUST NOT be written to `.env` files or baked into images. Under `--network=none`, secrets are provisioned in-memory via the Two-Tier Secrets architecture: Tier 1 infrastructure secrets in OCI Vault, Tier 2 runtime secrets via OpenBao (`bao agent` injecting secrets into `/dev/shm/secrets/` or passed via host-mediated environment injection at container spawn with short-TTL tokens). Long-lived secrets or plaintext environment files are strictly prohibited.

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
    image: ghcr.io/ecosystem/agent-runner:1.0.0
    runtime: runsc
    network_mode: none
    user: "1000:1000"
    read_only: true
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    
    # In-memory temporary scratch spaces (noexec, nosuid)
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=512m
      - /home/agent/.cache:rw,noexec,nosuid,size=1g
    
    volumes:
      # Isolated git worktree directory
      - /mnt/worktrees/task-1234:/workspace:rw
      
      # LiteLLM UNIX domain socket for LLM proxy calls
      - /var/run/litellm.sock:/var/run/litellm.sock:rw
      
      # OpenBao runtime machine credentials / token
      - /dev/shm/secrets/bao-token:/etc/openbao/token:ro
    
    environment:
      - WORKSPACE_DIR=/workspace
      - OPENAI_BASE_URL=http+unix://%2Fvar%2Frun%2Flitellm.sock/v1
      - OPENAI_API_KEY=unused-proxy-auth
      - LITELLM_SOCKET=/var/run/litellm.sock
    
    # In-memory secret injection entrypoint
    entrypoint: ["python3", "-m", "worker.run_task"]
```

---

## 4. Worktree CLI Execution Command Pattern

When dispatching an ephemeral task CLI runner from Temporal activities:

```bash
# Execute with OpenBao runtime credentials passed via secure RAM mount (/dev/shm)
docker run --rm \
    --runtime="${DOCKER_RUNTIME:-runsc}" \
    --network=none \
    --user="${UID:-1000}:${GID:-1000}" \
    --cap-drop=ALL \
    --security-opt=no-new-privileges:true \
    --read-only \
    --tmpfs /tmp:rw,noexec,nosuid,size=256m \
    --tmpfs /home/agent/.cache:rw,noexec,nosuid,size=512m \
    -v "/mnt/worktrees/${TASK_SLUG}:/workspace:rw" \
    -v "/var/run/litellm.sock:/var/run/litellm.sock:rw" \
    -e "OPENAI_BASE_URL=http+unix://%2Fvar%2Frun%2Flitellm.sock/v1" \
    ghcr.io/ecosystem/agent-runner:1.0.0 \
    python3 -m worker.execute_plan --worktree=/workspace
```

