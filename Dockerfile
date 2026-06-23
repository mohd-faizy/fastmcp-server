FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only the requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server source code
COPY server.py .

# Default environment variables (can be overridden at runtime)
ENV MCP_TRANSPORT=sse
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

# Expose the SSE port
EXPOSE 8000

# Run the MCP server (defaults to SSE mode via env vars)
CMD ["python", "server.py"]


# ──────────────────────────────────────────────────────────────
# Steps
# 1. base image
# 2. set work dir
# 3. copy requirements
# 4. install requirements
# 5. copy server code
# 6. set environment variables
# 7. expose port
# 8. run the server