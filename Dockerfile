FROM python:3.9-alpine3.18

LABEL mainainer="andresappdeveloper.com"

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /.venv && \
    /.venv/bin/pip install --upgrade pip setuptools wheel && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    /.venv/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /.venv/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser -u 5678 --disabled-password --gecos "" django-user && chown -R  django-user /app

ENV PATH="/.venv/bin:$PATH"

USER django-user

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi"]