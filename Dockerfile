FROM python:alpine3.20 as base

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

WORKDIR /app

# Update package lists, install bash, and cleanup cache
RUN apk update && \
    apk add bash && \
    pip install pipenv && \
    rm -rf /var/cache/apk/*

COPY Pipfile /app
COPY Pipfile.lock /app
RUN pipenv install --system

# Adding application files
ADD src /app/src

EXPOSE 8000/tcp
CMD ["python", "/src/main.py"]      