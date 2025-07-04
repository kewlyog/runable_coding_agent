FROM python:3.10-slim

WORKDIR /app/orchestration

COPY orchestration/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 5100

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "5100"]
