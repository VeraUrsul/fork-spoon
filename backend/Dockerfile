FROM python:3.10.12

WORKDIR /app

COPY requirements.txt .

RUN pip install -r /app/requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:7000", "fork_spoon.wsgi"]