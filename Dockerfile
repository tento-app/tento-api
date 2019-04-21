FROM python:3-alpine
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /code
COPY . /code
WORKDIR /code
RUN apk add --no-cache --virtual .build-deps \
    ca-certificates gcc postgresql-dev linux-headers musl-dev \
    libffi-dev jpeg-dev zlib-dev \
    && pip install -r requirements.txt
#CMD ["uwsgi","--ini","api/docker_uwsgi.ini"]