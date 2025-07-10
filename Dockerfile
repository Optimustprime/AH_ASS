FROM python:3.10-slim-buster
LABEL maintainer="AHASS"

ENV PYTHONUNBUFFERED=1

# Copy only the requirements files and install dependencies
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

RUN apt-get update && apt-get install -y \
    gcc g++ gnupg curl unixodbc-dev libjpeg-dev zlib1g-dev build-essential linux-headers-amd64 \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && python -m venv /py \
    && /py/bin/pip install --upgrade pip \
    && /py/bin/pip install -r /tmp/requirements.txt \
    && rm -rf /tmp

# Set environment variables
ENV PATH="/scripts:/py/bin:$PATH"

COPY ./scripts /scripts
COPY ./app /app

WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN if [ "$DEV" = "true" ]; then /py/bin/pip install -r /tmp/requirements.dev.txt ; fi && \
    adduser --disabled-password --no-create-home django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol && \
    chmod -R +x /scripts && \
    chown -R django-user:django-user /app

USER django-user

CMD ["run.sh"]