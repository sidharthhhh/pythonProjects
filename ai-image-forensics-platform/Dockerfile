FROM python:3.10

# Increment pip timeout to avoid ReadTimeoutError for large PyTorch wheels
ENV PIP_DEFAULT_TIMEOUT=1000

# Install system dependencies for OpenCV and python-magic
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/app

# Expose FastAPI port
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
