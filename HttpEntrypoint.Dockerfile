FROM python:3.7
RUN mkdir /usr/poetl
WORKDIR /usr/poetl

COPY ./src/HttpEntrypoint.py .
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 5000
ENTRYPOINT FLASK_APP=HttpEntrypoint.py flask run