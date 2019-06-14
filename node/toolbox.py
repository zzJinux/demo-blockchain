import requests

def bytes_to_hexstring(b):
    return ''.join('%02x' % x for x in b)


def bytes_leading_zero(bytes_len, n_zero_bits):
    barr = bytearray(bytes_len)
    n_skip = n_zero_bits // 8
    n_partial = n_zero_bits % 8
    
    if n_partial > 0:
        barr[n_partial] = (0b1 << (8 - n_partial)) - 1
        n_skip += 1
    
    for i in range(n_skip, bytes_len):
        barr[i] = 0xff

    return bytes(barr)

def mylog(text):
    print(text)
    # requests.post(url='http://localhost:8080', data=text)
