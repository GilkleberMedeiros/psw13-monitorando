FROM python:3.12.11-alpine3.22

# Install nginx and supervisor
RUN apk add --no-cache nginx supervisor

WORKDIR /app

COPY . .

RUN python3 -m pip install -r requirements.txt

# Copying  nginx config file 
COPY ./nginx.conf /etc/nginx/nginx.conf

# Copying supervisor config file 
COPY ./supervisord.conf /etc/supervisord.conf

RUN python3 manage.py collectstatic --no-input 

RUN python3 manage.py migrate 

EXPOSE 80

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]