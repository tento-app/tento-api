FROM python:3-alpine
ENV PYTHONUNBUFFERED 1
COPY . .
RUN apk add --no-cache --virtual .build-deps \
    ca-certificates gcc libmagic postgresql-dev linux-headers musl-dev \
    libffi-dev jpeg-dev zlib-dev \
    && pip install -r requirements.txt

ENV PORT 8000
# Expose ports
EXPOSE 8000

# CMD gunicorn config.wsgi -b 0.0.0.0:$PORT
CMD gunicorn --bind 0.0.0.0:$PORT api.wsgi