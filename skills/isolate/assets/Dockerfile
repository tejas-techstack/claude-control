# claude-control sandbox image — Claude Code in a container, host stays untouched.
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl git python3 python3-pip python3-venv ripgrep jq unzip nano \
    && rm -rf /var/lib/apt/lists/*
# Node (required by Claude Code)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && rm -rf /var/lib/apt/lists/*
RUN npm install -g @anthropic-ai/claude-code
RUN useradd -m -s /bin/bash sandbox
USER sandbox
WORKDIR /work
CMD ["/bin/bash"]
