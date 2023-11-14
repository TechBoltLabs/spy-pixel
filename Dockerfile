FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install gunicorn
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 80
ENV NAME World

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:80", "app:app"]
