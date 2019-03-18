import json
import falcon
import logging

from chariot_base.utilities import Traceable


db_name = 'fog_alerts'


def build_time_filter_clause(req):
    from_date = req.get_param('from') or None
    to_date = req.get_param('to') or None

    q = []
    if from_date is not None:
        q.append('\'%s\' <= time' % from_date)
    
    if to_date is not None:
        q.append('time <= \'%s\'' % to_date)

    return q


def build_pagination_clause(req):
    page = int(req.get_param('page') or 0)
    page_size = int(req.get_param_as_int('page_size') or 10)

    return page, page_size, 'LIMIT %s OFFSET %s' % (page_size, page * page_size)


def filter_by(req, filters=[]):
    time_clause = build_time_filter_clause(req)
    page, page_size, pagination_clause= build_pagination_clause(req)

    for clause in filters:
        time_clause.insert(0, '"%s"=\'%s\'' % (clause[0], clause[1]))

    if len(time_clause) > 0:
        q = 'SELECT * FROM "alerts" WHERE %s %s' % (' AND '.join(time_clause), pagination_clause)
    else:
        q = 'SELECT * FROM "alerts" %s' % (pagination_clause)

    logging.debug('Filter by: %s' % q)
    return page, page_size, q


def group_by_time(req, filters=[]):
    time_clause = build_time_filter_clause(req)
    interval = req.get_param('interval') or '1h'
    group_by_clause = 'GROUP BY time(%s)' % interval

    for clause in filters:
        time_clause.insert(0, '"%s"=\'%s\'' % (clause[0], clause[1]))

    if len(time_clause) > 0:
        q = 'SELECT COUNT(message) FROM "alerts" WHERE %s %s' % (' AND '.join(time_clause), group_by_clause)
    else:
        q = 'SELECT COUNT(message) FROM "alerts" %s' % (group_by_clause)

    logging.debug('Group by: %s' % q)
    return q


class AlertsResource(Traceable):

    def __init__(self, db):
        super(Traceable, self).__init__()
        self.tracer = None
        self.db = db

    def on_get(self, req, resp, sensor_id=None, alert_type=None):
        span = self.start_span_from_request('get_alerts', req)
        filters = []

        if sensor_id is not None:
            filters.append(['sensor_id', sensor_id])
            
        if alert_type is not None:
            filters.append(['name', alert_type])

        page, page_size, q = filter_by(req, filters)

        span.set_tag('q', q)
        span.set_tag('page', page)
        span.set_tag('page_size', page_size)

        results = self.db.query(q, db_name)
        results = list(results[('alerts', None)])

        resp.status = falcon.HTTP_200  # This is the default status
        resp.json = {
            'page': page,
            'size': len(results),
            'items': results
        }
        self.close_span(span)

    
class AlertOverTimeResource(Traceable):
    def __init__(self, db):
        super(Traceable, self).__init__()
        self.tracer = None
        self.db = db

    def on_get(self, req, resp, sensor_id=None, alert_type=None):
        span = self.start_span_from_request('get_alerts_overtime', req)
        filters = []

        if sensor_id is not None:
            filters.append(['sensor_id', sensor_id])
        
        if alert_type is not None:
            filters.append(['name', alert_type])


        q = group_by_time(req, filters)

        span.set_tag('q', q)

        results = self.db.query(q, db_name)
        results = list(results[('alerts', None)])

        resp.status = falcon.HTTP_200  # This is the default status
        resp.json = results
        self.close_span(span)
