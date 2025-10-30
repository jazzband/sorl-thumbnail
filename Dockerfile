FROM ubuntu:24.04

# Install dependencies including Python 3.9 and 3.12
RUN apt-get update && apt-get install -y \
    imagemagick \
    libgraphicsmagick1-dev \
    libgraphicsmagick++1-dev \
    graphicsmagick \
    libjpeg62 \
    zlib1g-dev \
    redis-server \
    libvips-tools \
    python3 \
    python3-pip \
    python3-venv \
    software-properties-common \
    lsof \
    && add-apt-repository ppa:deadsnakes/ppa -y \
    && apt-get update \
    && apt-get install -y python3.9 python3.9-venv python3.9-dev python3.12 python3.12-venv python3.12-dev \
    && rm -rf /var/lib/apt/lists/*

# Show ImageMagick version
RUN convert --version

WORKDIR /app

# Copy project files
COPY . /app/

# Install tox with gh-actions plugin and Pillow for debug scripts
RUN pip3 install --break-system-packages tox tox-gh-actions Pillow

# Usage:
# Build: docker build -f Dockerfile.test -t sorl-im6-test .
# Run all environments: docker run sorl-im6-test
# Run specific environment: docker run sorl-im6-test sh -c "redis-server --daemonize yes && tox -e py39-django42-imagemagick"

# Start Redis and run tox
CMD ["sh", "-c", "redis-server --daemonize yes && tox"]
