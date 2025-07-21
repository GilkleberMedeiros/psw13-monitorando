FROM python:3.12.11-alpine3.22

WORKDIR /app

COPY . .

RUN python3 -m pip install -r requirements.txt

RUN python3 manage.py collectstatic --no-input 

RUN python3 manage.py migrate 

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "home.wsgi"]