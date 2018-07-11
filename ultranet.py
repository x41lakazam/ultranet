import numpy as np
import struct
import math

def input():
    # return input
    pass

def chunks(l, n):

    for i in range(0, len(l), n):

        yield l[i:i+n]

def unpack(buf):
    chunk = list(chunks(buf, 2))
    return [struct.unpack('h', f)[0] for f in chunk]

def pack_bufer(buf):
    return [struct.pack('h', f) for f in buf]

def fft(sig):
    ft = np.fft.rfft(sig)
    return np.abs(ft)

def sig_peak(hertz, rate, chunk):
    h = hertz / rate
    return round(h*chunk)

def peak_weights(input, index, offset):
    output = []
    period = np.pi / (offset*2)

    for i in range(len(input)):
        if i >= index - offset and i <= index + offset:
            x = np.abs(np.sin((period * (i - index + offset)) + (np.pi / 2)))
            output.append(input[i] * x)

        else:
            output.append(0)

def has_frequency(fftsamp, freq, rate, chunk, offset=3):
    index = sig_peak(freq, rate, chunk)
    top = max(fftsamp[index-1:index+2])

    p_mean = np.average(peak_weights(fftsamp, index, offset))
    if top > p_mean:
        return fftsamp[index]
    else:
        return 0

def get_signal(buf):
    chunk = chunks(buf, 2)
    unpacked_bufer = [struct.unpack('h', f)[0] for f in chunk]
    return np.array(unpacked_bufer, dtype='float')

def raw_has_frequency(buf, freq, rate, chunk):
    fftsamp = fft(get_signal(buf))
    return has_frequency(fftsamp, freq, rate, chunk)

def get_freq_over_time(fftlist, search_freq, chunk=1024, rate=44100):
    return [has_frequency(fft, search_freq, rate, chunk) for fft in fftlist]

def get_points(fsamples, frame_size, threshold=None, last_point=0):
    points = []
    if threshold == None:
        threshold = np.median(fsamples)

    for i in range(len(fsamples)):
        freq = fsamples[i]
        point = 0
        if freq > threshold:
            if last_point == 1 or (i % frame_size) <= 2:
                point = 1
            else:
                point = 0

        points.append(point)
        last_point = point

    return points

def get_bits(points, frame_size):
    chunks = list(chunks(points, frame_size))
    return [round(sum(chunk) / frame_size) for chunk in chunks if len(chunk) == frame_size]

def get_bit(points, frame_size):
    return round(sum(points) / frame_size)

def get_bytes(bits, sigil):
    i = 0
    while i < len(bits) - len(sigil):
        if bits[i:i+len(sigil)] == sigil:
            i += len(sigil)
            break
        i+=1
    return [l for l in list(chunks(bits[i:],8)) if len(l) == 8]

def decode_byte(l):
    byte_str = ''.join([str(bit) for bit in l])
    return chr(int(byte_string, base=2))

def decode(bytes):
    string = ""
    for byte in bytes:
        byte = ''.join([str(bit) for bit in byte])
        string += chr(int(byte, base=2))
    return string

def tone(freq=400, datasize=4096, rate=44100, amp=12000.0, offset=0):
    sine = []
    for x in range(datasize):
        samp = math.sin(2*np.pi*freq*((x+offset)/rate))
        sine.append(int(samp*amp))

    return sine

def envelope(input, left=True, right=True, rate=44100):
    output = []

    half = len(input) / 2
    freq = np.pi / (len(input) / 2)

    for x in range(len(input)):
        samp = input[x]
        if (x < half and left) or (x >= half and right):
            samp *= (1 + math.sin(freq*x - (np.pi/2))) / 2

        output.append(int(samp))

    return output
