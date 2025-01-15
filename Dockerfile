# Use Alpine base image
FROM alpine:3.14

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies and Python
RUN apk add --no-cache \
    python3 \
    py3-pip \
    postgresql-client \
    postgresql-dev \
    gcc \
    g++ \
    python3-dev \
    musl-dev \
    libffi-dev \
    jpeg-dev \
    zlib-dev \
    linux-headers \
    netcat-openbsd

# Create symbolic links
RUN ln -sf python3 /usr/bin/python

# Upgrade pip and install packages
RUN python -m pip install --upgrade pip

# Copy requirements first to leverage Docker cache
COPY requirements.txt /app/

# Install packages
RUN pip install --no-cache-dir --ignore-installed -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
