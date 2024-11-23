FROM python:3.9-slim

# mkdir in docker container and enter it
WORKDIR /backend

# Copy /backend into the /backend in our docker container
COPY . /backend

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask default port within container to our machine
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]
