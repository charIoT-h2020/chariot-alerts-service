FROM registry.gitlab.com/chariot-h2020/chariot_base:latest

WORKDIR /usr/src/app

# Bundle app source
COPY . .

RUN python setup.py install

CMD ["python", "./chariot_alert_service/digester/alerts.py"]