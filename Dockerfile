FROM registry.gitlab.com/chariot-h2020/chariot_base:latest AS builder

WORKDIR /workspace

COPY . .

RUN apk add gnupg gcc g++ make python3-dev libffi-dev openssl-dev gmp-dev
RUN pip install -U pip && pip install pytest && pip install gunicorn
RUN pip install falcon-jsonify && python setup.py install

FROM python:3.7-alpine AS final
COPY --from=builder /usr/local/lib/python3.7 /usr/local/lib/python3.7
RUN apk add libffi-dev openssl-dev gmp-dev

WORKDIR /usr/src/app

COPY . .

RUN python setup.py install

CMD [ "python3", "-m", "chariot_alert_service.digester.alerts" ]