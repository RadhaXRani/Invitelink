FROM python:3.9

WORKDIR /app

COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 10000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:10000", "app:app"]
