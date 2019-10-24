import time

PAD_LABEL = "_PAD"
META_LABEL = "meta"

def bitslice(val, start, stop):
        return (val >> start) & ((1 << (stop - start)) - 1)

class PacketLayoutContext(object):
    def __init__(self):
        self.meta_byte_len = None
        self.meta_layout = []

        self.layout_byte_lens = {}
        self.layouts = {}

        self.frame_type_lookup = []

        self.resolve_lengths_with_pad()

    def resolve_layout_length_with_pad(self, layout):
        bit_len = 0
        for name, elm_bit_len in layout: 
            if name == PAD_LABEL:
                layout.remove((name, elm_bit_len))
                continue
            bit_len += elm_bit_len
        layout.append((PAD_LABEL, (8 - bit_len) % 8))
        return (bit_len + 7) // 8

    def resolve_lengths_with_pad(self):
        self.meta_byte_len = self.resolve_layout_length_with_pad(self.meta_layout)
        for layout_name, layout in self.layouts.iteritems(): 
            self.layout_byte_lens[layout_name] = self.resolve_layout_length_with_pad(layout)

    def get_layout_from_frame_type(self, frame_type):
        name = self.frame_type_lookup[frame_type]
        return (self.layouts[name], self.layout_byte_lens[name])

    def parse_config_line(self, line):
        token_list = line.split(" ")[1:]
        layout = []
        for i in xrange(0, len(token_list), 2):
            layout.append((token_list[i], int(token_list[i + 1])))
        return layout

    def configure_from_file(self, path):
        self.meta_layout = []
        self.layouts = {}
        with open(path, "r") as fd:
            for line in fd:
                line = line.strip()
                if line.startswith(META_LABEL):
                    self.meta_layout = self.parse_config_line(line)
                    continue
                layout_name = line[:line.index(" ")]
                self.layouts[layout_name] = self.parse_config_line(line)
        self.resolve_lengths_with_pad()

def packet_to_dict(raw, layout):
    packet_dict = {}
    bit_offset = 0
    byte_ind = 0
    for elm, bit_len in layout:
        val = bitslice(raw[byte_ind], max(8 - (bit_len + bit_offset), 0), 8 - bit_offset)
        bit_len -= 8 - bit_offset
        if bit_len <= 0:
            packet_dict[elm] = val
            bit_offset = 8 + bit_len
            continue
        while bit_len > 8:
            byte_ind += 1
            val <<= 8
            val |= raw[byte_ind]
            bit_len -= 8
        byte_ind += 1
        val <<= max(bit_len, 0)
        val |= bitslice(raw[byte_ind], 8 - bit_len, 8)
        packet_dict[elm] = val
        bit_offset = bit_len
    return packet_dict

def serialize_packet_dict(view, packet_dict, layout):
    bit_offset = 0
    for field, bit_len in layout:
        if bit_len == 0: continue
        field_view = view[:(bit_offset + bit_len + 7) // 8]
        temp_arr = bytearray(field_view)
        val = packet_dict[field] if field != PAD_LABEL else 0
        bit_len -= 8 - bit_offset
        ind = None
        if bit_len < 0: 
            temp_arr[0] |= val << (~bit_len + 1)
            bit_offset = 8 + bit_len
            ind = 0
        else: 
            temp_arr[0] |= val >> bit_len
            ind = 1
            while bit_len >= 8:
                bit_len -= 8
                temp_arr[ind] = (val >> bit_len) & 0xFF
                ind += 1
            if bit_len > 0: temp_arr[ind] = (val << (8 - bit_len)) & 0xFF
            bit_offset = bit_len
        field_view[:] = temp_arr
        view = view[ind:]