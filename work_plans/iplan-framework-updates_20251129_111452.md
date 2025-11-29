# IPLAN Framework Updates - Based on Code Review Findings

**Created**: 2025-11-29 11:14:52 EST
**Status**: Ready for Implementation
**Target**: `/opt/data/docs_flow_framework/ai_dev_flow/IPLAN/`
**Source Analysis**: Code review of `/opt/data/ibmcp/src/ibmcp/`

## Objective

Update IPLAN framework templates and validation rules to prevent code quality issues identified in the IB MCP Server code review. Add new checklists, validation gates, and pattern requirements.

## Code Review Findings Summary

| Category | Count | Impact |
|----------|-------|--------|
| Critical Issues | 0 | - |
| Major Issues | 7 | Missing imports, validation gaps |
| Minor Issues | 14 | Code quality improvements |
| Pattern Issues | 5 | Async/resource patterns |
| Documentation Issues | 3 | Docstrings, type hints |

## Root Cause Analysis

### Why These Issues Exist

| Issue Type | Root Cause | IPLAN Gap |
|------------|------------|-----------|
| Missing imports | No import verification step | No pre-execution syntax check requirement |
| Input validation gaps | No validation checklist | Missing security validation section |
| Code duplication | No utility search requirement | No "check existing code" step |
| Silent exception swallowing | No error handling standard | Missing exception handling rules |
| Mixed sync/async patterns | No async pattern guidance | No concurrency checklist |
| Thread safety issues | Wrong lock type selection | No lock selection guidance |
| Missing cleanup methods | No resource lifecycle rules | No cleanup/disposal requirements |
| `Optional[Any]` overuse | No type safety enforcement | Missing type hint quality gate |

---

## IPLAN Framework Updates Required

### Files to Update

| File | Update Type |
|------|-------------|
| `IPLAN-TEMPLATE.md` | Add 5 new checklist sections |
| `IPLAN_VALIDATION_RULES.md` | Add 12 new validation rules |
| `IPLAN_CREATION_RULES.md` | Add pattern requirements |

---

## Update 1: IPLAN-TEMPLATE.md - New Checklists

### Add Section 6.4: Pre-Implementation Checklist (NEW)

```markdown
### 6.4 Pre-Implementation Checklist

**MANDATORY** - Complete before writing code:

#### Code Reuse Search
- [ ] Search codebase for existing utilities: `grep -r "function_name" src/`
- [ ] Check for similar implementations in related modules
- [ ] Document reusable components found: ____________
- [ ] If duplicating code, document justification: ____________

#### Interface Definition
- [ ] Define Protocol/ABC interfaces before implementation
- [ ] Document interface contracts with type hints
- [ ] Specify return types for all public methods

#### Dependency Verification
- [ ] Verify all imports exist in project dependencies
- [ ] Check import compatibility with Python version
- [ ] Run syntax check: `python -m py_compile <file>`
```

### Add Section 6.5: Security Checklist (NEW)

```markdown
### 6.5 Security Checklist

**MANDATORY** for code handling external input:

#### Input Validation
- [ ] Validate all string inputs (empty, length, pattern)
- [ ] Validate numeric ranges (min, max, precision)
- [ ] Sanitize file paths (no path traversal)
- [ ] Validate identifiers (no empty strings, proper format)

#### Hash/Crypto Selection
- [ ] Document hash algorithm choice and rationale
- [ ] Use SHA-256+ for security-sensitive hashing
- [ ] MD5/SHA-1 only for non-security checksums (document why)

#### Credential Handling
- [ ] No credentials in code or logs
- [ ] Use environment variables or secrets manager
- [ ] Mask sensitive data in error messages
```

### Add Section 6.6: Error Handling Standard (NEW)

```markdown
### 6.6 Error Handling Standard

**MANDATORY** - All exception handling must follow:

#### Exception Rules
- [ ] NEVER use bare `except:` or `except Exception:` without re-raise
- [ ] Always use exception chaining: `raise NewError() from original`
- [ ] Log exceptions before handling: `logger.error("msg", exc_info=True)`
- [ ] Document retry behavior for recoverable errors

#### Required Pattern
```python
try:
    result = operation()
except SpecificError as e:
    logger.error("Operation failed: %s", e, exc_info=True)
    raise ServiceError("Descriptive message") from e
```

#### Prohibited Patterns
```python
# PROHIBITED - Silent swallowing
except Exception:
    pass

# PROHIBITED - No chaining
except ValueError:
    raise CustomError("msg")  # Missing 'from e'

# PROHIBITED - Bare except
except:
    return default_value
```
```

### Add Section 6.7: Async/Concurrency Checklist (NEW)

```markdown
### 6.7 Async/Concurrency Checklist

**MANDATORY** for async code:

#### Lock Selection
- [ ] Use `asyncio.Lock()` for async code (NOT `threading.Lock`)
- [ ] Use `threading.RLock()` only for sync code with reentrant needs
- [ ] Document lock scope and what it protects

#### Resource Management
- [ ] Implement `async with` context manager for resources
- [ ] Add cleanup/close methods for stateful classes
- [ ] Cancel pending tasks in cleanup: `task.cancel()`

#### Cache Patterns
- [ ] Add cache invalidation method
- [ ] Add cache clearing method
- [ ] Document TTL and eviction strategy
- [ ] Use `asyncio.Lock` for cache updates in async code

#### Required Pattern for Resources
```python
class ResourceManager:
    async def __aenter__(self):
        await self._acquire()
        return self

    async def __aexit__(self, *args):
        await self.cleanup()

    async def cleanup(self):
        """Release all resources."""
        # Cancel tasks, close connections, clear caches
```
```

### Add Section 6.8: Documentation Standard (NEW)

```markdown
### 6.8 Documentation Standard

**MANDATORY** for all public APIs:

#### Docstring Requirements
- [ ] All Protocol methods have docstrings with Args/Returns
- [ ] All public classes have class-level docstrings
- [ ] Complex algorithms have inline comments

#### Type Hint Quality
- [ ] NO `Any` type without documented justification
- [ ] Use specific types: `Optional[SpecificType]` not `Optional[Any]`
- [ ] Define TypeAlias for complex types
- [ ] Use Protocol for duck typing instead of Any

#### Module Documentation
- [ ] `__init__.py` has module docstring
- [ ] `__all__` exports are documented
- [ ] Usage examples in module docstring or README
```

---

## Update 2: IPLAN_VALIDATION_RULES.md - New Rules

### Add Rule 15: Import Verification (NEW)

```markdown
### 15. Import Verification

**Severity**: ERROR

**Rule**: All implementation phases must include import verification step.

**Required Command**:
```bash
python -m py_compile src/module/__init__.py
python -c "from module import *; print('Imports OK')"
```

**Validation**:
- [ ] `py_compile` check present in verification steps
- [ ] Import test command present after file creation
```

### Add Rule 16: Input Validation Gate (NEW)

```markdown
### 16. Input Validation Gate

**Severity**: ERROR

**Rule**: Functions accepting external input must validate:

**Checklist**:
- [ ] String parameters: empty check, length limit
- [ ] Numeric parameters: range validation with Pydantic `Field(ge=, le=)`
- [ ] Identifier parameters: format validation (no empty strings)
- [ ] File paths: existence check, path traversal prevention

**Prohibited**:
```python
# No validation
def process(data: str):
    return data.upper()

# With validation
def process(data: str):
    if not data or not data.strip():
        raise ValueError("Data cannot be empty")
    return data.upper()
```
```

### Add Rule 17: Exception Handling Gate (NEW)

```markdown
### 17. Exception Handling Gate

**Severity**: ERROR

**Rule**: Exception handlers must not silently swallow errors.

**Prohibited Patterns** (will fail validation):
- `except Exception: pass`
- `except: return None`
- `except ValueError: return default` (without logging)

**Required Pattern**:
```python
except SpecificError as e:
    logger.warning("Handled error: %s", e)
    return fallback_value
```
```

### Add Rule 18: Async Lock Verification (NEW)

```markdown
### 18. Async Lock Verification

**Severity**: WARNING

**Rule**: Async code must use `asyncio.Lock`, not `threading.Lock`.

**Check Command**:
```bash
grep -n "threading.Lock" src/**/*.py
# Should return empty for async modules
```

**Exception**: Sync-only modules may use threading locks (document reason).
```

### Add Rule 19: Resource Cleanup Verification (NEW)

```markdown
### 19. Resource Cleanup Verification

**Severity**: WARNING

**Rule**: Classes managing resources must implement cleanup.

**Required for**:
- Classes with `_cache` attributes
- Classes with `_connection` attributes
- Classes with background tasks
- Classes implementing `__aenter__`

**Verification**:
```bash
# Classes with cache should have clear_cache or cleanup method
grep -l "_cache" src/**/*.py | xargs grep -L "clear\|cleanup"
# Should return empty
```
```

### Add Rule 20: Type Hint Quality Gate (NEW)

```markdown
### 20. Type Hint Quality Gate

**Severity**: WARNING

**Rule**: Minimize use of `Any` type.

**Check Command**:
```bash
grep -n "Optional\[Any\]" src/**/*.py
grep -n ": Any" src/**/*.py
# Each occurrence must have documented justification
```

**Acceptable Uses**:
- Third-party library objects without stubs
- Dynamic plugin systems
- Must add comment: `# Any: reason`
```

### Add Rule 21: Code Duplication Check (NEW)

```markdown
### 21. Code Duplication Check

**Severity**: INFO

**Rule**: Before implementing utility functions, search for existing implementations.

**Required Step**:
```bash
# Search for similar function names
grep -r "function_name" src/

# Search for similar patterns
grep -r "pattern" src/
```

**Document**: If similar code exists, document why new implementation needed.
```

---

## Update 3: IPLAN_CREATION_RULES.md - Pattern Requirements

### Add Section: Required Patterns (NEW)

```markdown
## Required Implementation Patterns

### Error Handling Pattern

All error handling must follow this pattern:

```python
try:
    result = await operation()
except SpecificError as e:
    logger.error("Context: %s", e, exc_info=True)
    raise DomainError("User-friendly message") from e
except Exception as e:
    logger.exception("Unexpected error in operation")
    raise
```

### Resource Management Pattern

Classes managing external resources must implement:

```python
class Service:
    async def __aenter__(self) -> "Service":
        return self

    async def __aexit__(self, *args) -> None:
        await self.cleanup()

    async def cleanup(self) -> None:
        """Release resources. Safe to call multiple times."""
        if self._cache:
            self._cache.clear()
        if self._tasks:
            for task in self._tasks:
                task.cancel()
```

### Validation Pattern

Input validation must use Pydantic or explicit checks:

```python
# Pydantic approach (preferred)
class Config(BaseModel):
    timeout: float = Field(ge=1.0, le=300.0)
    name: str = Field(min_length=1, max_length=100)

# Manual approach (when Pydantic not suitable)
def validate_input(value: str) -> str:
    if not value or not value.strip():
        raise ValueError("Value cannot be empty")
    if len(value) > MAX_LENGTH:
        raise ValueError(f"Value exceeds {MAX_LENGTH} characters")
    return value.strip()
```

### Async Cache Pattern

Caches in async code must use async locks:

```python
class CachedService:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._lock = asyncio.Lock()  # NOT threading.Lock

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            return self._cache.get(key)

    async def set(self, key: str, value: Any) -> None:
        async with self._lock:
            self._cache[key] = value

    def clear(self) -> int:
        """Clear cache. Returns count of items cleared."""
        count = len(self._cache)
        self._cache.clear()
        return count
```
```

---

## Execution Plan

### Phase 1: Update IPLAN-TEMPLATE.md
Add sections 6.4-6.8 (5 new checklists)

### Phase 2: Update IPLAN_VALIDATION_RULES.md
Add rules 15-21 (7 new validation rules)

### Phase 3: Update IPLAN_CREATION_RULES.md
Add Required Patterns section

### Phase 4: Validate Changes
Run validation on existing IPLAN files to ensure compatibility
