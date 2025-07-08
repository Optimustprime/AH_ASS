FROM python:3.10-alpine3.13
LABEL maintainer="DATACHEF"

ENV PYTHONUNBUFFERED=1

# Copy only the requirements files and install dependencies
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev libstdc++ && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev linux-headers && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp && \
    apk del .tmp-build-deps

# Set environment variables
ENV PATH="/scripts:/py/bin:$PATH"

# Copy the rest of the files
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

RUN pytest

USER django-user

CMD ["run.sh"]
