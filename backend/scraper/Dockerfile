# UNUSED

# # Use the Playwright base image
# FROM mcr.microsoft.com/playwright:v1.39.0-focal

# # Set the working directory
# WORKDIR /app/scraper

# # Ensure Python and pip are installed and accessible
# RUN apt-get update -y && \
#     apt-get install -y python3-pip && \
#     if [ ! -e /usr/bin/python ]; then ln -s /usr/bin/python3 /usr/bin/python; fi && \
#     if [ ! -e /usr/bin/pip ]; then ln -s /usr/bin/pip3 /usr/bin/pip; fi

# # Update pip to the latest version using pip3 directly
# RUN pip3 install --upgrade pip

# # Install necessary dependencies
# RUN apt-get update -y && \
#     apt-get install -y \
#     g++ \
#     make \
#     cmake \
#     unzip \
#     libcurl4-openssl-dev \
#     autoconf \
#     libtool \
#     libnss3 \
#     libatk-bridge2.0-0 \
#     libx11-xcb1 \
#     libxcb-dri3-0 \
#     libdrm2 \
#     libgbm1 \
#     libasound2 \
#     libatk1.0-0 \
#     libcups2 \
#     libdbus-1-3 \
#     libxrandr2 \
#     libxss1 \
#     libxtst6 \
#     xdg-utils \
#     wget \
#     ca-certificates \
#     fonts-liberation \
#     libappindicator3-1 \
#     libdbusmenu-gtk3-4 \
#     libgdk-pixbuf2.0-0

# # Copy requirements and install dependencies
# COPY requirements.txt .
# RUN pip3 install -r requirements.txt

# # Install Playwright and its browsers during the build
# RUN npx playwright install --with-deps chromium
# RUN playwright install

# # Copy the scraper script
# COPY . .

# # Debug chromium (error with playwright install)
# # RUN ls -l /root/.cache/ms-playwright/

# # Set default command
# CMD python scraper.py && tail -f /dev/null
