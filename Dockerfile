FROM ubuntu:latest
FROM python:3.10-slim-buster

EXPOSE 27017

COPY . /app
WORKDIR /app
RUN pip install Flask
RUN pip install pymongo

CMD [ "python3", "app.py" ]
