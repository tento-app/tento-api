FROM python:3-alpine
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /code
COPY . /code
WORKDIR /code
RUN apk add --no-cache --virtual .build-deps \
    ca-certificates gcc libmagic postgresql-dev linux-headers musl-dev \
    libffi-dev jpeg-dev zlib-dev \
    && pip install -r requirements.txt
# Expose ports
EXPOSE 8000
# CMD ["uwsgi", "--ini", "api/dokcer_uwsgi.ini", "--daemonize", "uwsgi.log", "--pidfile", "uwsgi.pid"]
# CMD ["uwsgi", "--ini", "api/dokcer_uwsgi.ini"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]