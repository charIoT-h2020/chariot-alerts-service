FROM python:3.6-alpine
VOLUME ["/usr/src/app"]
WORKDIR /usr/src/app

# Bundle app source
COPY . .

EXPOSE 8030

RUN apk add gnupg gcc g++ make python3-dev libffi-dev openssl-dev gmp-dev && pip install falcon-jsonify gunicorn pytest && python setup.py install

ENTRYPOINT ["/usr/local/bin/gunicorn", "--config", "/usr/src/app/gunicorn.py", "chariot_alert_service.app:app"]
