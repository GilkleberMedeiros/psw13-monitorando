FROM python:3.12.11-alpine3.22

WORKDIR /app

COPY . .

RUN python3 -m pip install -r requirements.txt

EXPOSE 80

CMD ["python3", "manage.py", "runserver", "0.0.0.0:80"]