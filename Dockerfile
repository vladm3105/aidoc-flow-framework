FROM python:3.11-slim

# Set working directory
WORKDIR /opt/data/docs_flow_framework

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3-pip \
    python3.11-venv

# Create Python virtual environment
RUN python3.11 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Install Python dependencies
COPY scripts/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY AUTOPILOT/scripts/requirements.txt .
RUN pip install --no-cache-dir -r AUTOPILOT/scripts/requirements.txt

# Create work directory
RUN mkdir -p /workspace/work_plans

# Set up environment
ENV PYTHONPATH=/opt/data/docs_flow_framework:/opt/venv/lib/python3.11/site-packages

# Default command
CMD ["python3", "-u", "AUTOPILOT/scripts/mvp_autopilot.py", "--help"]
