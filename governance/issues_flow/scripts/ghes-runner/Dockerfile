FROM ubuntu:22.04

ARG RUNNER_VERSION=2.311.0
ARG RUNNER_ARCH=x64
ARG GHES_RUNNER_URL=""
ARG DEBIAN_FRONTEND=noninteractive

# Core dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl git jq sudo unzip wget gnupg lsb-release \
    build-essential libssl-dev libffi-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev libncurses-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 3.10, 3.11, 3.12 via deadsnakes PPA
RUN apt-get update && apt-get install -y --no-install-recommends software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa -y \
    && apt-get update && apt-get install -y --no-install-recommends \
    python3.10 python3.10-venv python3.10-dev \
    python3.11 python3.11-venv python3.11-dev \
    python3.12 python3.12-venv python3.12-dev \
    && rm -rf /var/lib/apt/lists/*

# pip for each Python version
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10 \
    && curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11 \
    && curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12

# Default python3 -> 3.11 (matches most workflow steps)
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Node.js 20 LTS (actions runtime)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Docker CLI (for container actions — uses host Docker socket)
RUN install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
    > /etc/apt/sources.list.d/docker.list \
    && apt-get update && apt-get install -y --no-install-recommends docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
    > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

# Runner user (non-root)
RUN useradd -m -s /bin/bash runner \
    && echo "runner ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
    && usermod -aG docker runner 2>/dev/null || true

# GitHub Actions runner binary — download from GHES if URL provided, else github.com
WORKDIR /home/runner/actions-runner
RUN if [ -n "${GHES_RUNNER_URL}" ]; then \
        echo "Downloading runner from GHES: ${GHES_RUNNER_URL}" && \
        curl -fsSL -o actions-runner.tar.gz "${GHES_RUNNER_URL}"; \
    else \
        echo "Downloading runner from github.com v${RUNNER_VERSION}" && \
        curl -fsSL -o actions-runner.tar.gz \
            "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz"; \
    fi \
    && tar xzf actions-runner.tar.gz \
    && rm actions-runner.tar.gz \
    && ./bin/installdependencies.sh \
    && chown -R runner:runner /home/runner

COPY start.sh /home/runner/start.sh
RUN chmod +x /home/runner/start.sh

USER runner
WORKDIR /home/runner/actions-runner

ENTRYPOINT ["/home/runner/start.sh"]
