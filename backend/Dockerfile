FROM python:3.9-slim

# mkdir in docker container and enter it
WORKDIR /backend

# Copy /backend into the /backend in our docker container
COPY . /backend

# Install system dependencies required by Playwright
RUN apt-get update -y && \
    apt-get install -y \
    g++ \
    make \
    cmake \
    unzip \
    libcurl4-openssl-dev \
    autoconf \
    libtool \
    libnss3 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libdrm2 \
    libgbm1 \
    libasound2 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    wget \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libdbusmenu-gtk3-4 \
    libgdk-pixbuf2.0-0

# Install Python dependencies
# - --no-cache-dir is used because we want the latest libraries always, so we can't cache it
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and its browser dependencies
RUN pip install playwright
RUN playwright install

# Expose the Flask default port within container to our machine
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]
