from ipaddress import ip_address
import socket
from .crypto import get_key,keccak256
import gevent
import select
import rlp
import ecdsa


class Discovery(object):
    def __init__(self):
        self.sk = get_key('private.txt')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', self.endpoint.udpPort))
        # set socket non-blocking mode
        self.sock.setblocking(0)

    def wrap_packet(self, packet):
        payload= packet.packet_type + rlp.encode(packet.pack())
        sig = ecdsa.SigningKey.from_pem(self.sk).sign(payload)
        payload_hash= keccak256(sig)
        return payload_hash+sig

    def run(self):
        gevent.spawn(self.listen)

    def listen(self):
        while True:
            ready = select([self.sock], [], [], 1.0)
            if ready[0]:
                data, addr = self.sock.recvfrom(2048)
                gevent.spawn(self.receive, data, addr)

    def receive(self, data, addr):
        pass
    def send(self,packet,node):
        pass
    def ping(self, endpoint):
        pass
