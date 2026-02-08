FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 7860

# Start Xvfb FIRST, then FastAPI
CMD Xvfb :99 -screen 0 1920x1080x24 & \
    uvicorn main:app --host 0.0.0.0 --port 7860