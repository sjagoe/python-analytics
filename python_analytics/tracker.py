from __future__ import absolute_import, unicode_literals

import requests
import uuid

from six import add_metaclass, text_type
from six.moves.urllib import parse

from .event_encoder import TrackedAttribute, EventEncoder
from .utils import get_user_agent


class _AnalyticsHandler(object):

    target = 'https://ssl.google-analytics.com/collect'

    def __init__(self, session=None):
        if session is None:
            session = requests.Session()

        session.headers['User-Agent'] = get_user_agent(
            session.headers.get('User-Agent'))

        self._session = session

    def send(self, data):
        encoded_data = parse.urlencode(data, encoding='utf-8')
        response = self._session.post(self.target, data=encoded_data)
        response.raise_for_status()


@add_metaclass(EventEncoder)
class Tracker(object):

    version = TrackedAttribute('v', int)
    tracking_id = TrackedAttribute('tid', text_type)
    client_id = TrackedAttribute('cid', text_type)

    def __init__(self, tracking_id, requests_session=None):
        self._handler = _AnalyticsHandler(session=requests_session)
        self.version = 1
        self.tracking_id = tracking_id
        self.client_id = text_type(uuid.uuid4())

    def send(self, event):
        data = self.to_dict()
        data.update(event.to_dict())
        self._handler.send(data)
