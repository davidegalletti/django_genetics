import json, logging
from urllib.request import urlopen
from _datetime import datetime

logger = logging.getLogger(__name__)


def json_serial(obj):
    """
        JSON serializer for objects not serializable by default json code
    """
    if isinstance( obj, datetime ):
        serial = obj.isoformat( )
        return serial
    raise TypeError( "Type not serializable" )


class ApiInvoker:
    FAILURE = "Failure"
    SUCCESS = "Success"

    def __init__(self, url=None, auto=True):
        self.url = url
        self.decoded = None
        self.exception = None
        self.response = None
        self.status = None
        if self.url:
            self.invoke()

    def invoke(self):
        self.status = None
        self.response = None
        self.exception = None
        try:
            if self.url:
                logger.debug('ApiInvoker url      %s' % self.url)
                response = urlopen(self.url)
                self.response = response.read().decode("utf-8")
                logger.debug('ApiInvoker response %s' % self.response)
                self.parse()
                self.status = ApiInvoker.SUCCESS
        except Exception as ex:
            logger.error('ApiInvoker invoke %s' % str(ex))
            self.exception = ex
            self.status = ApiInvoker.FAILURE

    def parse(self):
        self.decoded = None
        self.exception = None
        try:
            self.decoded = json.loads(self.response)
        except Exception as ex:
            logger.error('ApiInvoker parse %s' % str(ex))
            self.exception = ex

    def json_response(self):
        return json.dumps( {"status": self.status, "response": self.decoded}, sort_keys=False, default=json_serial )
