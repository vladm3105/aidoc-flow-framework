# AIDOC Ecosystem Authentication Standard

**Status:** Approved Standard v1.0  
**Target Scope:** All `aidoc-*` spoke repositories (`aidoc-flow-*`, `aidoc-observability-monitoring`, `aidoc-hybrid-ci`, etc.)  
**Companion Documents:**
- [`platform-identity`](../../platform-identity/README.md) — Canonical Identity Repository (Blueprints, SDK, Tests)
- [`06-security-rbac.md`](../../technology_stack/06-security-rbac.md) — Platform RBAC & Two-Tier Secrets
- [`27-customer-and-agent-identity.md`](../../technology_stack/27-customer-and-agent-identity.md) — Four Identity Planes Architecture

---

## 1. Executive Summary

All authentication across the AIDOC ecosystem is governed by the central **Identity Plane** ([`platform-identity`](../../platform-identity/README.md)) running Authentik. Individual spoke projects must **never** roll custom authentication schemes, store plaintext credentials, or issue ad-hoc tokens.

Every AIDOC service implements authentication according to its operational surface:

| Surface | Protocol / Pattern | Enforcing Component | Identity Plane |
|---|---|---|---|
| **Human Web UIs** (HyperDX, Bytebase, LiteLLM Admin) | Forward-Auth Outpost / OIDC SSO | Traefik v3 / Cloudflare Access | **Plane W** (Workforce) |
| **Microservice REST / gRPC APIs** | Bearer JWT verified against JWKS | `client/jwks.py` / PyJWT / Go `jwt-go` | **Plane W / M** |
| **AI Agent Runs** (LangGraph / Temporal) | RFC 8693 Delegation Token over mTLS | `client/delegation.py` helper | **Plane A** (Agent) |
| **Telemetry Ingest** (OTel Collector) | Network namespace isolation / OTLP | Private mesh (`platform-mesh`) | **Data Plane** |
| **Continuous Integration** (Hybrid-CI) | Ephemeral Runner OIDC Federation | OpenBao JWT Auth / Cloudflare Service Tokens | **Plane M** (Workload) |

---

## 2. API Authentication Pattern (FastAPI / Python Spokes)

Spoke microservices verify caller JWTs **statelessly** using Authentik's public JWKS endpoint. Services do not hold database connections to Authentik or shared HMAC secrets.

### Installation
Add `platform-identity` client to your repository's dependencies or copy [`client/jwks.py`](../../platform-identity/client/jwks.py):

```toml
# pyproject.toml
dependencies = [
    "PyJWT[crypto]>=2.8.0",
    "cryptography>=42.0.0",
]
```

### FastAPI Middleware Implementation

```python
from fastapi import FastAPI, Depends, Security, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from client.jwks import JWKSValidator, AuthenticationError, TokenClaims

app = FastAPI()
bearer_scheme = HTTPBearer(auto_error=True)

# 1. Initialize thread-safe cached validator
validator = JWKSValidator(
    jwks_url="https://auth-stage.aiops-flow.io/application/o/my-service/.well-known/jwks.json",
    issuer="https://auth-stage.aiops-flow.io/application/o/my-service/",
    audience="aidoc-service-audience",
    lifespan=300, # 5 min JWKS cache
)

async def require_authenticated_user(
    auth: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> TokenClaims:
    try:
        return validator.validate_token(auth.credentials)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

# 2. Protect routes with RBAC group enforcement (Doc 06 §5.2)
@app.get("/api/v1/resource")
async def get_resource(claims: TokenClaims = Depends(require_authenticated_user)):
    # Verify allowed RBAC roles
    allowed = {"developer", "project-admin", "platform-admin"}
    if not set(claims.groups).intersection(allowed):
        raise HTTPException(status_code=403, detail="Insufficient group permissions")
    
    return {"status": "ok", "user": claims.sub, "roles": claims.groups}
```

---

## 3. Web UI Protection (Forward-Auth Pattern)

For internal web tools and consoles (e.g., HyperDX, Coroot, Superset, Bytebase):
* Do **not** build custom login pages.
* Attach the Authentik Forward-Auth Outpost middleware to the Traefik router or Cloudflare Access application.
* Authentik validates user identity, evaluates WebAuthn MFA, and forwards authenticated claims upstream:
  * `X-authentik-username`
  * `X-authentik-email`
  * `X-authentik-groups`

---

## 4. AI Agent Delegation (Plane A Invariants)

When an AI agent in a Temporal workflow or LangGraph execution calls tools (MCP servers, APIs):
1. **Never pass user tokens into workflow history:** Workflow definitions pass execution context references (`run_id`, `project`, `consent_id`), never cleartext access tokens.
2. **Activity-Side Exchange:** The activity worker uses [`client/delegation.py`](../../platform-identity/client/delegation.py) to narrow scopes strictly to what the target tool requires.
3. **Mandatory Consent for `execute`:** Any effectful tool action (database migrations, git pushes, payment actions) requires a valid human `consent_id`.
4. **Transport Constraint:** Delegation tokens are Bearer JWTs presented over **mandatory mTLS** to the tool gateway.
5. **Bounded TTL:** Delegation tokens expire in $\le 15\text{ minutes}$ (`MAX_TTL = 900s`).

---

## 5. Local CI Invariant (Offline Fast Inner Loop)

Per [`aidoc-hybrid-ci`](../../aidoc-hybrid-ci/README.md), fast inner-loop checks (`task check` <15s, `task ci` <45s) **must never depend on the live stage Authentik instance**.

* Local unit tests mock the JWKS response using synthetic RSA key pairs (see [`tests/test_jwks.py`](../../platform-identity/tests/test_jwks.py)).
* Staging integration tests verify the live Authentik OIDC discovery endpoint during outer-loop E2E pipeline executions.
