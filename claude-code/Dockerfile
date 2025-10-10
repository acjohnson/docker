FROM node:22-trixie

ENV DEBIAN_FRONTEND=noninteractive

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
        git \
        tig \
        vim \
        iproute2 \
        netcat-openbsd \
        python3-pip \
        python3-virtualenv \
        python3-pytest && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /

# Default command
CMD ["bash"]
