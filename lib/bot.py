import hashlib
import lib.event
import logging
import queue
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

    def __init__(self, host, port=6667, encoding='utf-8', use_ssl=False,
                 ca_certs=None, known_hosts=None, max_reconnects=5, db=None):
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
        self.db = db
        self._buffer = ''
        self._socket = None
        self._msg_queue = queue.Queue()
        self._log = logging.getLogger(__name__)

    def _create_socket(self, use_ssl):
        """Create a TCP socket and adds in SSL if requested."""
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
            sha512_hash = hashlib.sha512(cert).hexdigest()
            if self.host in self.known_hosts:
                hash_ = self.known_hosts[self.host]
                if sha512_hash != hash_:
                    self.disconnect()
                    e = ('SSL certificate does not match the one from the '
                         'known_hosts file. Most likely the server has changed'
                         ' its certificate and you have to delete the old line'
                         ' from the known_hosts file. Be careful, this could '
                         'also mean that you are being attacked!\nOld hash: '
                         '%s\nNew hash: %s' % (hash_, sha512_hash))
                    raise ssl.CertificateError(e)
            else:
                self.disconnect()
                raise UnknownCertError(self.host, sha512_hash,
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
                self._log.warning('Connection refused, retrying in %ds.' %
                                  time_sleep)
                time.sleep(time_sleep)
                retries += 1
            else:
                connected = True
        if self.use_ssl:
            self._validate_ssl_cert()
        lib.event.call('connected', {'bot': self})

    def reconnect(self):
        """Reconnect with the same credentials as before."""
        self.disconnect()
        self.connect()

    def disconnect(self):
        """Disconnect from a server if a connection is open."""
        if self._socket is not None:
            self._socket.close()

    def data_available(self):
        """Check if data is available on the socket with a timeout."""
        rlist, _, __ = select.select([self._socket], [], [], self.timeout)
        return self._socket in rlist

    def _send(self):
        """Consume the internal message queue and send msgs to the server."""
        if self._msg_queue.qsize() > 0:
            self._socket.sendall(self._msg_queue.get() + b'\r\n')

    def send(self, msg):
        """Append a message to an internal messaging queue.

        If the message contains multiple commands, it will be throttled.
        """
        for line in msg.strip().split('\r\n'):
            self._msg_queue.put(line.encode(self.encoding, 'replace'))

    def _handle_data(self, data):
        """Buffer, decode and process incoming data."""
        self._buffer += data.decode(self.encoding, 'replace')
        if '\r\n' in self._buffer:
            messages = self._buffer.split('\r\n')
            for message in messages[:-1]:
                lib.event.call('raw_message', {'bot': self, 'msg': message})
            self._buffer = messages[-1].rstrip()

    def loop(self):
        self.connect()
        while True:
            if self.data_available():
                data = self._socket.recv(4096)
                if not data:
                    self._log.warning('Empty response: Reconnecting the bot.')
                    self.reconnect()
                    continue
                self._handle_data(data)
            self._send()
            lib.event.call('watchdog_tick', {'bot': self})
