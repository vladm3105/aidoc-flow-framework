# Python Environment Setup on Systems with Conda

## The Problem

On systems that have both `/opt/anaconda` (or any conda installation) and a
system Python, `pyenv install` frequently fails when building Python 3.12+.
The build succeeds but the final `pip` bootstrap step dies:

```
Installing pip from https://bootstrap.pypa.io/get-pip.py...
curl: /opt/anaconda/lib/libcurl.so.4: no version information available (required by curl)
error: failed to install pip via get-pip.py

AttributeError: 'datetime.datetime' object has no attribute 'tb_frame'
```

Root cause: conda's `libcurl.so.4` shadows the system curl, and the conda
Python's `xmlrpc` module has an ABI mismatch with the freshly built 3.12
interpreter used to bootstrap pip.

## The Solution

**Use conda to create the environment directly** — it's already on the system
and avoids the self-bootstrap problem entirely.

```bash
/opt/anaconda/bin/conda create -p /path/to/project/.venv python=3.12.13 -y
```

The resulting environment lives at `<project>/.venv/bin/python` and works
identically to a venv or pyenv install.

### Checking for Conda

```bash
ls /opt/anaconda/bin/conda  # most common location
find /opt -maxdepth 3 -name "conda" -type f 2>/dev/null
```

### Fallback If Conda Is Not Available

Install pyenv build dependencies first:

```bash
sudo apt-get install -y build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev libncursesw5-dev \
  xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

Then temporarily unset conda from PATH before building:

```bash
PATH=$(echo "$PATH" | tr ':' '\n' | grep -v anaconda | tr '\n' ':')
pyenv install 3.12.13
```

## When to Use Which

| Project Type | Preferred Method |
|-------------|-----------------|
| SDD project (needs yaml, hashlib) | conda create (fast, no build) |
| CI/CD container (no conda) | pyenv or apt install python3.12 |
| User wants specific patch version | conda create with `python=3.12.13` |
