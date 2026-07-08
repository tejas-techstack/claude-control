# claude-control sandbox image — Claude Code in a container, host stays untouched.
# Pinned base + non-root user. Uncomment the stack layer(s) your project needs;
# keep the image lean by only adding what you use.
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ARG NODE_MAJOR=22

# Base toolchain: git, python, ripgrep, jq — enough for most repos.
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl git python3 python3-pip python3-venv ripgrep jq unzip nano \
    && rm -rf /var/lib/apt/lists/*

# Node — required by Claude Code itself.
RUN curl -fsSL "https://deb.nodesource.com/setup_${NODE_MAJOR}.x" | bash - && \
    apt-get install -y nodejs && rm -rf /var/lib/apt/lists/*
RUN npm install -g @anthropic-ai/claude-code

# --- optional stack layers (uncomment what the project needs) ----------------
# C/C++ build tools:
# RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
# Go:
# RUN curl -fsSL https://go.dev/dl/go1.22.5.linux-amd64.tar.gz | tar -C /usr/local -xz
# ENV PATH="/usr/local/go/bin:${PATH}"
# Rust (installed per-user below, so place after USER sandbox if you prefer):
# RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
# Java:
# RUN apt-get update && apt-get install -y --no-install-recommends default-jdk && rm -rf /var/lib/apt/lists/*
# -----------------------------------------------------------------------------

# Non-root user — Claude runs as this, never root.
RUN useradd -m -s /bin/bash sandbox
USER sandbox
WORKDIR /work

# Credentials persist in the mounted named volume (/home/sandbox), never on the host project.
CMD ["/bin/bash"]
