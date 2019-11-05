from ipaddress import ip_address
import struct
from .crypto import keccak256


class Endpoint(object):
    def __init__(self, address, udpport, tcpport):
        if isinstance(address, bytes) and len(address) > 4:
            address = address.decode('utf8')
        self.address = ip_address(address)
        self.tcpPort = tcpport
        self.udpPort = udpport

    def pack(self):
        return [
            self.address.packed,
            struct.pack('>H', self.udpPort),
            struct.pack('>H', self.tcpPort),
        ]

    @classmethod
    def unpack(cls, endpoint):
        udpPort = struct.unpack('>H', endpoint[1])[0]
        if endpoint[2] == '':
            tcpPort = udpPort
        else:
            tcpPort = struct.unpack('>H', endpoint[2])[0]
        return cls(endpoint[0], udpPort, tcpPort)


class PingNode(object):
    packet_type = '\x01'
    version = '\x04'

    def __init__(self, endpoint_from, endpoint_to, timestamp):
        self.endpoint_from = endpoint_from
        self.endpoint_to = endpoint_to
        self.timestamp = timestamp

    def pack(self):
        return [
            self.version,
            self.endpoint_from.pack(),
            self.endpoint_to.pack(),
            struct.pack('>I', self.timestamp)
        ]

    @classmethod
    def unpack(cls, packed):
        endpoint_from = Endpoint.unpack(packed[1])
        endpoint_to = Endpoint.unpack(packed[2])
        timestamp = struct.unpack('>I', packed[3])[0]
        return cls(endpoint_from, endpoint_to, timestamp)


class Pong(object):
    packet_type = '\x02'

    def __init__(self, to, echo, timestamp):
        self.to = to
        self.echo = echo
        self.timestamp = timestamp

    def pack(self):
        return [
            self.to.pack(),
            self.echo,
            struct.pack('>I', self.timestamp)
        ]

    @classmethod
    def unpack(cls, packed):
        to = Endpoint.unpack(packed[0])
        echo = packed[1]
        timestamp = struct.unpack('>I', packed[2])[0]
        return cls(to, echo, timestamp)


class FindNeighbors(object):
    packet_type = '\x03'

    def __init__(self, target, timestamp):
        self.target = target
        self.timestamp = timestamp

    def pack(self):
        return [
            self.target,
            struct.pack('>I', self.timestamp)
        ]

    @classmethod
    def unpack(cls, packed):
        timestamp = struct.unpack('>I', packed[1])[0]
        return cls(packed[0], timestamp)


class Neighbors(object):
    packet_type = '\x04'

    def __init__(self, nodes, timestamp):
        self.nodes = nodes
        self.timestamp = timestamp

    def pack(self):
        return [
            map(lambda x: x.pack(), self.nodes),
            struct.pack('>I', self.timestamp)
        ]

    @classmethod
    def unpack(cls, packed):
        nodes = map(lambda x: Node.unpack(x), packed[0])
        timestamp = struct.unpack('>I', packed[1])[0]
        return cls(nodes, timestamp)


class Node(object):
    def __init__(self, endpoint, node_key):
        self.endpoint = endpoint
        self.node_key = node_key
        self.node_id = keccak256(self.node_key)

    def pack(self):
        packed = self.endpoint.pack()
        packed.append(self.node_key)
        return packed

    @classmethod
    def unpack(cls, packed):
        endpoint = Endpoint.unpack(packed[0:3])
        return cls(endpoint, packed[3])
