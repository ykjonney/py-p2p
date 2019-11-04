from ipaddress import ip_address
import struct



class Endpoint(object):
    def __init__(self,address,udpport,tcpport):
        if isinstance(address, bytes) and len(address) > 4:
            address = address.decode('utf8')
        self.address=ip_address(address)
        self.tcpPort=tcpport
        self.udpPort=udpport

    def pack(self):
       return [
           self.address.packed,
           struct.pack('>H',self.udpPort)
           struct.pack('>H',self.tcpPort),   
       ]

    @classmethod
    def unpack(cls,endpoint):
        udpPort=struct.unpack('>H',endpoint[1])[0]
        if endpoint[2]=='':
            tcpPort=udpPort
        tcpPort=struct.unpack('>H',endpoint[2])[0]
        return cls(endpoint[0],udpPort,tcpPort)
 
class PingNode(object):
    packet_type = '\x01'
    version = '\x04'
    def __init__(self,endpoint_from,endpoint_to,timestamp):
        self.endpoint_from=endpoint_from
        self.endpoint_to=endpoint_to
        self.timestamp=timestamp
    
    def pack():
        return [
            self.version,
            self.endpoint_from.pack(),
            self.endpoint_to.pack(),
            struct.pack('>I',self.timestamp)
        ]
    
    @classmethod
    def unpack(cls,packed):
        endpoint_from=Endpoint.unpack(packed[1])
        endpoint_to=Endpoint.unpack(packed[2])
        timestamp=struct.unpack('>I',packed[3])[0]
        return cls(endpoint_from,endpoint_to,timestamp)


class Pong(object):
    packet_type = '\x02'
    def __init__(self,to,echo,timestamp):
        self.to=to
        self.echo=echo
        self.timestamp=timestamp
    def pack(self):
        return [
            self.to.pack(),
            self.echo,
            struct.pack('>I',self.timestamp)
        ]   
    @classmethod         
    def unpack(cls,packed):
        to=Endpoint.unpack(packed[0])
        echo=packed[1]
        timestamp=struct.unpack('>I',packed[2])[0]
        return cls(to,echo,timestamp)