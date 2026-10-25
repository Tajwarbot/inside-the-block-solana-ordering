FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY obp ./obp
ENV OBP_DATA=/data
ENTRYPOINT ["python", "-m", "obp"]
