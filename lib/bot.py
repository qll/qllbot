import hashlib
import logging
import select
import socket
import ssl
import time


class BotError(Exception):
    pass


class UnknownCertError(Exception):
    """Raised when a previously unknown certificate is encountered.

    Only used with the known_hosts SSL authentication method.
    """

    def __init__(self, host, sha512_hash, sha1_hash):
        self.host = host
        self.sha512_hash = sha512_hash
        self.sha1_hash = sha1_hash


class Bot(object):
    """Handles network communication of the bot."""

    timeout = 1
    watchdog_threshold = 120

    def __init__(self, host, port=6667, encoding='utf-8', use_ssl=False,
                 ca_certs=None, known_hosts=None, max_reconnects=5):
        if use_ssl and ca_certs is None and known_hosts is None:
            raise BotError('Expecting either ca_certs or known_hosts to be '
                           'set when SSL is enabled.')
        self.host = host
        self.port = port
        self.encoding = encoding
        self.use_ssl = use_ssl
        self.ca_certs = ca_certs
        self.known_hosts = known_hosts
        self.max_reconnects = max_reconnects
        self._buffer = ''
        self._socket = None

    def _create_socket(self, use_ssl):
        """Creates a TCP socket and adds in SSL if requested."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if use_ssl:
            cert_reqs = ssl.CERT_REQUIRED if self.ca_certs else ssl.CERT_NONE
            s = ssl.wrap_socket(s, cert_reqs=cert_reqs, ca_certs=self.ca_certs)
        return s

    def _validate_ssl_cert(self):
        if self.ca_certs is not None:
            cert = self._socket.getpeercert()  # get cert as dictionary
            ssl.match_hostname(cert, self.host)
        else:
            cert = self._socket.getpeercert(True)  # get binary cert
            if self.host in self.known_hosts:
                hash_ = self.known_hosts[self.host]
                if hashlib.sha512(cert).hexdigest() != hash_:
                    self.disconnect()
                    raise ssl.CertificateError('SSL certificate does not match'
                                               'the one saved in the known '
                                               'hosts storage.')
            else:
                self.disconnect()
                raise UnknownCertError(self.host,
                                       hashlib.sha512(cert).hexdigest(),
                                       hashlib.sha1(cert).hexdigest())

    def connect(self):
        """Connect to a server. Retry if it is not available."""
        connected = False
        retries = 0
        while not connected:
            try:
                self._socket = self._create_socket(self.use_ssl)
                self._socket.connect((self.host, self.port))
            except ConnectionRefusedError:
                if retries >= self.max_reconnects:
                    raise
                time_sleep = (2 ** retries) * 5
                logging.debug('Connection refused, retrying in %ds.' %
                              time_sleep)
                time.sleep(time_sleep)
                retries += 1
            else:
                connected = True
        if self.use_ssl:
            self._validate_ssl_cert()

    def reconnect(self):
        """Reconnect with the same credentials as before."""
        self.disconnect()
        self.connect()

    def disconnect(self):
        """Disconnect from a server if a connection is open."""
        if self._socket is not None:
            self._socket.close()

    def data_available(self):
        """Checks if data is available on the socket with a timeout."""
        rlist, _, __ = select.select([self._socket], [], [], self.timeout)
        return self._socket in rlist

    def send(self, msg):
        """Send data to server after applying the specified encoding."""
        self._socket.sendall(msg.encode(self.encoding, 'replace') + b'\r\n')

    def _handle_data(self, data):
        """Buffer, decode and process incoming data."""
        self._buffer += data.decode(self.encoding, 'replace')
        if '\r\n' in self._buffer:
            messages = self._buffer.split('\r\n')
            for message in messages[:-1]:
                log.debug(message)
                # self.client.parse(message)
            self._buffer = messages[-1].rstrip()

    def _call_watchdog(self):
        """Is executed roughly all watchdog_treshold seconds."""
        pass
        # if sent_ping:
        #     # server answered slower than watchdog_threshold seconds
        #     self.reconnect()
        #     sent_ping = False
        # else:
        #     self.send('PING :fuugg')
        #     sent_ping = True

    def loop(self):
        self.connect()
        watchdog_counter = 0
        while True:
            if self.data_available():
                data = self._socket.recv(4096)
                if not data:
                    self.reconnect()
                    watchdog_counter = 0
                    continue
                else:
                    self._handle_data(data)
            watchdog_counter += 1
            if watchdog_counter > self.watchdog_threshold:
                watchdog_counter = 0
                self._call_watchdog()
