import select
import socket
import ssl
import time


HOST, PORT = 'chat.freenode.net', 7000


class BotError(Exception):
    pass


class UnknownCertError(Exception):
    """Raised when a previously unknown certificate is encountered.

    Only used with the known_hosts SSL authentication method.
    """

    def __init__(self, host, sha1_fingerprint, md5_fingerprint):
        self.host = host
        self.sha1_fingerprint = sha1_fingerprint
        self.md5_fingerprint = md5_fingerprint


class Bot(object):
    """Handles network communication of the bot."""

    timeout = 1
    watchdog_threshold = 120

    def __init__(self, host, port=6667, use_ssl=False, ca_certs=None,
                 known_hosts=None, max_reconnects=5):
        if use_ssl and ca_certs is None and known_hosts is None:
            raise BotError('Expecting either ca_certs or known_hosts to be '
                           'set when SSL is enabled.')
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.ca_certs = ca_certs
        self.known_hosts = known_hosts
        self.max_reconnects = max_reconnects
        self._socket = None

    def _create_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.use_ssl:
            cert_reqs = ssl.CERT_REQUIRED if self.ca_certs else ssl.CERT_NONE
            s = ssl.wrap_socket(s, cert_reqs=cert_reqs, ca_certs=self.ca_certs)
        return s

    def connect(self):
        """ Connect to a server. Retry if it is not available. """
        connected = False
        retries = 0
        while not connected:
            try:
                self._socket = self._create_socket()
                self._socket.connect((self.host, self.port))
            except ConnectionRefusedError:
                if retries >= self.max_reconnects:
                    print('No connection possible, sorry :(')
                    raise
                time_sleep = (2 ** retries) * 5
                print('Connection refused, retrying in %ds.' % time_sleep)
                time.sleep(time_sleep)
                retries += 1
            else:
                connected = True

    def reconnect(self):
        """ Reconnect to a server with host and port. """
        self.disconnect()
        self.connect()

    def disconnect(self):
        """ Disconnect from a server if a connection is open. """
        if self._socket:
            self._socket.close()

    def data_available(self):
        """ Checks if data is available on the socket w/ a timeout. """
        rlist, _, __ = select.select([self._socket], [], [], self.timeout)
        return self._socket in rlist

    def send(self, msg):
        self._socket.sendall(msg.encode('utf-8', 'replace') + b'\r\n')

    def loop(self):
        self.connect()
        watchdog_counter = 0
        sent_ping = False
        while True:
            if self.data_available():
                data = self._socket.recv(4096)
                print(data)
                if not data:
                    self.reconnect()
            watchdog_counter += 1
            if watchdog_counter > self.watchdog_threshold:
                watchdog_counter = 0
                if sent_ping:
                    # server answered slower than watchdog_threshold seconds
                    self.reconnect()
                    sent_ping = False
                else:
                    self.send('PING :fuugg')
                    sent_ping = True


class IRC(object):
    def __init__(self):
        pass


if __name__ == '__main__':
    bot = Bot(HOST, PORT, use_ssl=True, known_hosts={})
    bot.loop()
