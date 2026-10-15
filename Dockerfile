FROM python:3.11-slim

# LibreOffice, ffmpeg va shriftlar (PDF va audio konvertatsiyasi uchun zarur)
RUN apt-get update && apt-get install -y \
    libreoffice \
    ffmpeg \
    fonts-dejavu-core \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PORT=10000
EXPOSE 10000

CMD ["python", "-u", "main.py"]

