FROM ubuntu:latest
FROM python:3.10-slim

EXPOSE 27017

COPY . /app
WORKDIR /app
RUN pip3 install Flask
RUN pip3 install pymongo

CMD [ "python3", "app.py" ]
