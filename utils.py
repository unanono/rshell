import re


def extract_ip_mask_ifconfig(addr_line):
    ip = re.findall(r"inet addr:\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}", addr_line)
    if ip and len(ip[0].split(":")) > 1:
        ip = ip[0].split(":")[1]
    mask = re.findall(r"Mask:\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}", addr_line)
    bits = 0
    if mask and len(mask[0].split(":")) > 1:
        mask = mask[0].split(":")[1]
        import math

        octets = mask.split(".")
        for o in octets:
            mo = int(o)
            if mo > 0:
                bits += int(math.log(mo, 2)) + 1
    return ip, bits


def is_private_ip(ip):
    octets = ip.split(".")
    f = False
    if len(octets) == 4:
        o1 = int(octets[0])
        o2 = int(octets[1])
        if o1 == 10:
            f = True
        elif o1 == 172 and (16 <= o2 <= 31):
            f = True
        elif o1 == 192 and o2 == 168:
            f = True
        elif o1 == 169 and o2 == 254:
            f = True
        else:
            f = False
    return f
