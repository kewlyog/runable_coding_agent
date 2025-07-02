# --- Base image
FROM ubuntu:22.04

# --- Environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:1
ENV LANG=C.UTF-8
ENV PYTHONPATH=/home/agent
ENV PATH="/home/agent/node_modules/.bin:/usr/local/bin:${PATH}"
ENV NODE_PATH="/home/agent/node_modules"

# --- Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    xvfb x11vnc xdotool fluxbox \
    wget curl git sudo \
    net-tools lsof \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# --- Install Node.js (LTS) and npm
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

# --- Install noVNC
RUN mkdir -p /opt/novnc/utils/websockify && \
    wget -qO- https://github.com/novnc/noVNC/archive/refs/tags/v1.4.0.tar.gz | tar xz --strip 1 -C /opt/novnc && \
    wget -qO- https://github.com/novnc/websockify/archive/refs/tags/v0.10.0.tar.gz | tar xz --strip 1 -C /opt/novnc/utils/websockify

# --- Install Jupyter and dev tools
RUN pip3 install --upgrade pip && \
    pip3 install jupyterlab notebook jupyter uvicorn fastapi python-multipart openai python-dotenv && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g typescript@latest ts-node@latest

# --- Install additional tools
RUN npm install -g typescript@latest ts-node@latest

# --- Create user for security
RUN useradd -ms /bin/bash agent && \
    echo "agent ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER agent
WORKDIR /home/agent

# --- Expose ports
# 5901: VNC, 6080: noVNC, 8888: Jupyter, 5000: Agent API
EXPOSE 5901 6080 8888 5000

# --- Supervisor config
USER root
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
USER agent

# --- Entrypoint
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

COPY . /home/agent
RUN npm install ts-node typescript

WORKDIR /home/agent 