FROM python:3.13-slim

WORKDIR /project

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY . .

WORKDIR /project/backend
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
