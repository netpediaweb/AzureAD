FROM python:3.12-slim


# Set work directory

WORKDIR /app


# Install OS dependencies

RUN apt-get update && apt-get install -y \

    libldap2-dev libsasl2-dev libssl-dev gcc \

    build-essential libffi-dev \

    && apt-get clean


# Copy and install Python dependencies

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


# Copy app files

COPY . .


# Expose port

EXPOSE 5000


# Run app

CMD ["python", "app.py"]

