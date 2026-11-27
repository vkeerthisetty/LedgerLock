FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt* ./
RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null || pip install --no-cache-dir fastapi uvicorn cryptography
COPY . .
ENV PORT=8080
ENV APP_ENV=cloud-run
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
