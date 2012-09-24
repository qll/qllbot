import socket
import ssl
import hashlib
import lib.logging as log
from lib.irc import Client
from lib.singleton import Singleton


class Bot(Singleton):
	def init(self, nickname, realname, ident, password, channels, use_ssl = False, ca_cert = None, encoding = 'utf-8'):
		self.use_ssl  = use_ssl
		self.ca_cert  = ca_cert
		self.client   = Client(self, nickname, realname, ident, password)
		self.channels = channels
		self.encoding = encoding
		self.buffer   = ''

	def create_socket(self):
		""" Create a socket and wrap a SSL layer around it if required. """
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if self.use_ssl:
			cert_reqs = ssl.CERT_REQUIRED if self.ca_cert else ssl.CERT_NONE
			self.irc = ssl.wrap_socket(self.sock, cert_reqs = cert_reqs, ca_certs = self.ca_cert) 
		else:
			self.irc = self.sock

	def connect(self, host, port, known_hosts = None):
		""" 
		Connects to an IRC server.
		
		If used with use_ssl enabled, then it expects a dictionary of known
		hosts with the respective SHA1 fingerprint of the certificate, like:

			{'chat.freenode.net': 'cd1dc6658dd3905ad5735676879aeebd69ce75f2'}

		This function will raise an UnknownCertException if the certificate is
		unknown and a InvalidCertException if the certificate changed.
		"""
		self.create_socket()
		if self.use_ssl and not self.ca_cert and not isinstance(known_hosts, dict):
			raise Exception('Please provide a dictionary of known hosts if you use SSL without specifing a CA certificate.')
		self.irc.connect((host, port))
		if self.use_ssl:
			if self.ca_cert:
				cert = self.irc.getpeercert() # get cert as dictionary
				ssl.match_hostname(cert, host)
			else:
				cert = self.irc.getpeercert(True) # get cert in binary representation
				if host in known_hosts:
					if hashlib.sha1(cert).hexdigest() != known_hosts[host]:
						self.disconnect()
						raise InvalidCertException()
				else:
					self.disconnect()
					raise UnknownCertException(
						host,
						hashlib.sha1(cert).hexdigest(),
						hashlib.md5(cert).hexdigest()
					)
		self.client.identify(host)
		for channel, password in self.channels.items():
			self.client.join(channel, password)
	
	def disconnect(self):
		""" Disconnects from the IRC server. """
		self.irc.close()
	
	def send(self, message):
		self.irc.send((message + '\r\n').encode(self.encoding))
	
	def loop(self):
		""" Constantly recieves data from the socket (blocking) and writes it to the buffer. """
		while True:
			self.buffer += self.irc.recv(1024).decode(self.encoding, 'replace')
			if '\r\n' in self.buffer:
				messages = self.buffer.split('\r\n')
				for message in messages[:-1]:
					log.debug(message)
					self.client.parse(message)
				self.buffer = messages[-1].rstrip()


class UnknownCertException(Exception):
	def __init__(self, host, sha1_fingerprint, md5_fingerprint):
		""" Takes and saves informations about the unknown certificate. """
		self.host = host
		self.sha1_fingerprint = sha1_fingerprint
		self.md5_fingerprint = md5_fingerprint


class InvalidCertException(Exception):
	pass
