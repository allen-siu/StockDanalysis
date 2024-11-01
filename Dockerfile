FROM python:3.10.12

ENV PYTHONBUFFED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
EXPOSE 8501


