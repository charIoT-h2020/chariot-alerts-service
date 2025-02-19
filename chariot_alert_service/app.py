# Let's get this party started!
import falcon
import logging
import falcon_jsonify

from chariot_base.utilities import open_config_file
from chariot_base.datasource import LocalDataSource

from chariot_base.utilities import Tracer
from chariot_alert_service import __service_name__
from chariot_alert_service.resources.alerts import AlertsResource, AlertOverTimeResource
from wsgiref import simple_server

# falcon.API instances are callable WSGI apps
app = falcon.API(middleware=[
    falcon_jsonify.Middleware(help_messages=True),
])


opts = open_config_file()

options_db = opts.local_storage
options_tracer = opts.tracer
options_alert_digester = opts.alert_digester

options_db['database'] = options_alert_digester['database']
logging.debug(f'Database setup: {options_db}')
db = LocalDataSource(**options_db)

# Resources are represented by long-lived class instances
alerts = AlertsResource(db)
alerts_over_time = AlertOverTimeResource(db)

if options_tracer['enabled']:
    options_tracer['service'] = __service_name__
    logging.debug(f'Enabling tracing for service "{__service_name__}"')
    tracer = Tracer(options_tracer)
    tracer.init_tracer()
    alerts.inject_tracer(tracer)
    alerts_over_time.inject_tracer(tracer)

app.add_route('/alerts', alerts)
app.add_route('/alerts/sensor/{sensor_id}', alerts)
app.add_route('/alerts/type/{alert_type}', alerts)
app.add_route('/alerts/sensor/{sensor_id}/type/{alert_type}', alerts)

app.add_route('/alerts/overtime', alerts_over_time)
app.add_route('/alerts/overtime/sensor/{sensor_id}', alerts_over_time)
app.add_route('/alerts/overtime/type/{alert_type}', alerts_over_time)
app.add_route(
    '/alerts/overtime/sensor/{sensor_id}/type/{alert_type}', alerts_over_time)


if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 9000, app)
    httpd.serve_forever()
