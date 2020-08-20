# -*- coding: utf-8 -*-
import os
import uuid
import json
import gmqtt
import asyncio
import signal
import datetime
import logging
import logging.config

from chariot_base.connector import LocalConnector
from chariot_base.utilities import open_config_file
from chariot_base.datasource import LocalDataSource
from chariot_base.model import DataPoint
from chariot_alert_service import __version__, __service_name__


class AlertDigester(LocalConnector):
    def __init__(self, options):
        super(AlertDigester, self).__init__()
        self.local_storage = None

        self.table = options['table']
        self.database = options['database']
        self.client_id = options['client_id']
        self.topics = []

    def on_message(self, client, topic, payload, qos, properties):
        decoded_msg = json.loads(payload)
        span = self.start_span_from_message('on_message', decoded_msg)
        if 'uber-trace-id' in decoded_msg:
            del decoded_msg['uber-trace-id']
        logging.debug(decoded_msg)
        decoded_msg['id'] = str(uuid.uuid4())
        point = DataPoint(self.database, self.table, decoded_msg)
        if 'timestamp' in decoded_msg:
            point.timestamp = decoded_msg['timestamp']
            del decoded_msg['timestamp']
        else:
            point.timestamp = datetime.datetime.utcnow().isoformat()

        self.local_storage.publish(point)

        span.set_tag('is_ok', True)
        self.close_span(span)

    def set_up_local_storage(self, options):
        options['database'] = self.database
        self.local_storage = LocalDataSource(
            **options
        )

    def on_connect(self, client, flags, rc, properties=None):
        self.connected = True
        self.connack = (flags, rc, properties)
        if rc == 0:
            self.subscribe_to_topics()

    def set_topics(self, topics):
        self.topics = topics

    def subscribe_to_topics(self):
        subscriptions = []
        for topic in self.topics:
            subscriptions.append(gmqtt.Subscription(topic, qos=2))
        self.client.subscribe(subscriptions, subscription_identifier=1)
        logging.info('Waiting for raised alerts...')


STOP = asyncio.Event()


def ask_exit(*args):
    logging.info('Stoping....')
    STOP.set()


async def main(args=None):
    opts = open_config_file()

    options_mqtt = opts.brokers.northbound
    options_alert_digester = opts.alert_digester
    options_db = opts.local_storage
    options_tracer = opts.tracer

    options_alert_digester['client_id'] = uuid.uuid4()

    client = gmqtt.Client(f"{__service_name__}_{options_alert_digester['client_id']}", clean_session=True)
    await client.connect(host=options_mqtt['host'], port=options_mqtt['port'], version=4)

    logger = AlertDigester(options_alert_digester)

    logger.register_for_client(client)
    logger.set_up_local_storage(options_db)

    if options_tracer['enabled'] is True:
        options_tracer['service'] = __service_name__
        logging.info(f'Enabling tracing for service "{__service_name__}"')
        logger.set_up_tracer(options_tracer)

    logger.set_topics([options_alert_digester['listen']])
    logger.subscribe_to_topics()
    await STOP.wait()
    await client.disconnect()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    loop.add_signal_handler(signal.SIGINT, ask_exit)
    loop.add_signal_handler(signal.SIGTERM, ask_exit)

    loop.run_until_complete(main())
    logging.info('Stopped....')
