FROM python:3.10-slim

WORKDIR /app

COPY main.py ./

RUN pip install flask requests prometheus_client

CMD ["python", "main.py"]