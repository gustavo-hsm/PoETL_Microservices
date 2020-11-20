FROM python:3.7
RUN mkdir /usr/poetl
WORKDIR /usr/poetl

COPY ./src/service/ .
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt