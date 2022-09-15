FROM python:3.10.5-slim

WORKDIR /src
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app/

WORKDIR /src/
RUN python3 -m uvicorn app.main:app --host 0.0.0.0 --port 80
