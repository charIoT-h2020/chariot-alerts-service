# Let's get this party started!
import falcon
import falcon_jsonify

from chariot_base.datasource import LocalDataSource 

from resources.alerts import AlertsResource, AlertOverTimeResource

# falcon.API instances are callable WSGI apps
app = falcon.API(middleware=[
    falcon_jsonify.Middleware(help_messages=True),
])


db = LocalDataSource('192.168.2.24', 8086, 'root', 'root', 'fog_alerts')

# Resources are represented by long-lived class instances
alerts = AlertsResource(db)
alerts_over_time = AlertOverTimeResource(db)

app.add_route('/alerts', alerts)
app.add_route('/alerts/sensor/{sensor_id}', alerts)
app.add_route('/alerts/type/{alert_type}', alerts)
app.add_route('/alerts/sensor/{sensor_id}/type/{alert_type}', alerts)

app.add_route('/alerts/overtime', alerts_over_time)
app.add_route('/alerts/overtime/sensor/{sensor_id}', alerts_over_time)
app.add_route('/alerts/overtime/type/{alert_type}', alerts_over_time)
app.add_route('/alerts/overtime/sensor/{sensor_id}/type/{alert_type}', alerts_over_time)