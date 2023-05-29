FROM python:3.10-slim

WORKDIR /app

COPY foodgram_api/requirements.txt .

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt --no-cache-dir

COPY backend/foodgram_api/ .

CMD ["gunicorn", "foodgram_api.wsgi:application", "--bind", "0:8000" ]