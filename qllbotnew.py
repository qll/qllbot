import select
import socket
import time


HOST, PORT = 'localhost', 5000


class Bot(object):
    timeout = 1
    watchdog_threshold = 120

    def __init__(self, host, port, max_retries=5):
        self.host = host
        self.port = port
        self.max_retries = max_retries
        self.socket = None

    def connect(self):
        """ Connect to a server. Retry if it is not available. """
        connected = False
        retries = 0
        while not connected:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
            except ConnectionRefusedError:
                if retries >= self.max_retries:
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
        if self.socket:
            self.socket.close()

    def data_available(self):
        """ Checks if data is available on the socket w/ a timeout. """
        rlist, _, __ = select.select([self.socket], [], [], self.timeout)
        return self.socket in rlist

    def send(self, msg):
        self.socket.sendall(msg.encode('utf-8', 'replace') + b'\r\n')

    def loop(self):
        self.connect()
        watchdog_counter = 0
        sent_ping = False
        while True:
            if self.data_available():
                data = self.socket.recv(4096)
                if not data:
                    self.reconnect()
            watchdog_counter += 1
            if watchdog_counter > self.watchdog_threshold:
                if sent_ping:
                    # server answered slower than watchdog_threshold seconds
                    self.reconnect()
                    sent_ping = False
                else:
                    self.send('PING :fuugg')
                    sent_ping = True
                watchdog_counter = 0


class IRC(object):
    def __init__(self):
        pass


if __name__ == '__main__':
    bot = Bot(HOST, PORT)
    bot.loop()
