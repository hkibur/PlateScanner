import json

def from_packet_type(packet_raw):
    raw_dict = json.loads(packet_raw.decode())
    packet_class = PACKET_LOOKUP_TABLE[raw_dict["__ptype__"].lower()]
    packet = packet_class()
    packet.fields = raw_dict
    return packet

class ShieldPacket(object):

    packet_type_lookup = []

    def __init__(self):
        self.fields = {}

    def get_raw(self):
        return json.dumps(self.fields).encode()

    def __setitem__(self, field, value):
        self.fields[field] = value

    def __getitem__(self, field):
        return self.fields[field]

class ReadyPacket(ShieldPacket):
    __ptype__ = "ready"

PACKET_LOOKUP_TABLE = {
    "ready": ReadyPacket,
}