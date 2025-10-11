FROM node:22-trixie

ENV DEBIAN_FRONTEND=noninteractive

ARG GO_VERSION=1.25.2
ARG GO_SHA256=d7fa7f8fbd16263aa2501d681b11f972a5fd8e811f7b10cb9b26d031a3d7454b

# Ensure latest apt updates installed
RUN apt-get update && \
    apt-get dist-upgrade -y --no-install-recommends

# Install claude-code
RUN npm install -g @anthropic-ai/claude-code

# Install Docker
RUN apt-get update && \
    apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release && \
    install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | \
        gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    chmod a+r /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
        $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Install additional tools
RUN apt-get update && \
    apt-get install -y \
        sudo \
        git \
        tig \
        vim \
        jq \
        iproute2 \
        netcat-openbsd \
        python3-pip \
        python3-venv \
        python3-virtualenv \
        python3-pytest && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Golang
RUN curl -fsSL "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz" -o go.tar.gz && \
    echo "${GO_SHA256}  go.tar.gz" | sha256sum -c - && \
    tar -C /usr/local -xzf go.tar.gz && \
    rm go.tar.gz && \
    ln -s /usr/local/go/bin/go /usr/local/bin/go && \
    ln -s /usr/local/go/bin/gofmt /usr/local/bin/gofmt

# Configure sudoers for passwordless sudo
RUN echo "node ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/node && \
    chmod 0440 /etc/sudoers.d/node

# Set working directory
WORKDIR /

# Default command
CMD ["bash"]
