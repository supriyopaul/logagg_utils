import time
import atexit

from tornado import gen
import tornado.ioloop
import tornado.web

import requests
from nsq.reader import Reader
from basescript import BaseScript
import Queue
from deeputil import generate_random_string


class NsqAPI(tornado.web.RequestHandler):

    NSQ_MAX_IN_FLIGHT = 2500
    CHANNEL_NAME_LENGTH = 6
    DELETE_CHANNEL_URL = 'http://{}/channel/delete?topic={}&channel={}'

    def initialize(self, log):

        self.log = log

    def _parse_query(self, query_arguments):
        '''
        query_arguments: {'topic': ['Heartbeat'], 'nsqd_tcp_address': ['195.201.98.142:4150']}
        '''

        nsqd_tcp_addresses=query_arguments['nsqd_tcp_address']
        topic = query_arguments['topic'][0]

        return nsqd_tcp_addresses, topic

    def _remove_channel(self, nsqd_host,
            topic, channel):
        '''
        Delete a Nsq channel
        '''

        nsqd_http_port = '4151'
        nsqd_http_address = nsqd_host + ':' + nsqd_http_port

        requests.post(self.DELETE_CHANNEL_URL.format(nsqd_http_address,
            topic, channel))

    @gen.coroutine
    def get(self):
        '''
        Sample uri: /tail?nsqd_tcp_address=195.201.98.142:4150&topic=Heartbeat
        '''
        loop = tornado.ioloop.IOLoop.current()

        nsqd_tcp_addresses, topic = self._parse_query(self.request.query_arguments)
        channel = generate_random_string(self.CHANNEL_NAME_LENGTH)
        nsqd_host = nsqd_tcp_addresses[0].split(':')[0]


        nsq_reader = Reader(nsqd_tcp_addresses=nsqd_tcp_addresses,
                topic=topic,
                channel=channel,
                max_in_flight=self.NSQ_MAX_IN_FLIGHT)

        for msg in nsq_reader:

            if self.request.connection.stream.closed():
                # Cleanup
                nsq_reader.close()
                self._remove_channel(nsqd_host=nsqd_host,
                        topic=topic, channel=channel)
                self.log.info('channel_created', channel=channel)
                break
            self.write(msg.body)
            yield self.flush()
            msg.fin()

        self.finish()


class NsqServer(BaseScript):
    NAME = 'NsqServer'
    DESC = 'Reads nsq topics'

    def prepare_api(self):
        return tornado.web.Application([
        (r'/tail', NsqAPI,
        dict(log=self.log)),
        ])

    def start(self):
        app = self.prepare_api()
        app.listen(self.args.port)

        try:
            tornado.ioloop.IOLoop.current().start()
        except KeyboardInterrupt:
            # FIXME: cleanup if exited
            self.log.info('exiting')



    def define_subcommands(self, subcommands):
        super(NsqServer, self).define_subcommands(subcommands)

        runserver_cmd = subcommands.add_parser('runserver',
                help='NsqServer Service')

        runserver_cmd.set_defaults(func=self.start)

        runserver_cmd.add_argument('-p', '--port',
                default=1077,
                help='NsqServer port')

def main():
    NsqServer().start()

if __name__ == '__main__':
    main()
