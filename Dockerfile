FROM python:3.10.5-slim

WORKDIR /src
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["pytest"]
