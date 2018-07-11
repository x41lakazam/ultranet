import pyaudio
import sys
import osi1
import queue
import threading
import time
import numpy as np
#my imports
import setup
import ultranet


class Listener(object):

    def __init__(self,
                 frame_size,
                 chunk,
                 listen_freq,
                 rate,
                 sigil_opts,
                 input_size,
                 threshold={'bot':None, 'up':None},
                 format=pyaudio.paInt16
                 ):

        self.format = format
        self.frame_size = frame_size
        self.chunk = chunk
        self.frames_pbuffer = chunk*10
        self.listen_freq = listen_freq
        self.rate = rate
        self.sigil = [int(o) for o in sigil_opts]
        self.input_size = input_size

        # Set queues

        self.input_frames = queue.Queue(input_size) # raw data
        self.points       = queue.Queue(input_size) # ftt value at a certain frequency
        self.bits         = queue.Queue(input_size/frame_size)

        self.processes    = [self.input_frames, self.points, self.bits]
        # Set timeouts
        self.timeout = {'default':0.1,
                        'sample':None,
                        'frames':None,
                        'points':None,
                        'bytes' :None,
                        'different_bit_boundary':3}
        # Set all None values to default
        self.timeout = {x:self.timeout['default'] for x in self.timeout.keys() if not self.timeout[x]}

        self.threshold = threshold

    def start_processes(self):
        for process in self.processes:
            thread = threading.Thread(target=process)
            thread.daemon = True
            thread.start()

    def frames_processing(self):
        while True:
            try:
                frame = self.input_frames.get(False)
                fft   = ultranet.fft(frame)
                point = ultranet.has_frequency(fft, self.listen_freq, self.rate, self.chunk)
                self.points.put(point)

            except Queue.Empty:
                time.sleep(self.timeout['frames'])

    def points_processing(self):
        while True:
            currents = []
            while len(currents) < frame_size:
                try:
                    currents.append(points.get(False))
                except queue.Empty:
                    time.sleep(self.timeout['points'])

            while 1:
                while np.average(currents) > self.threshold['bot']:
                    try:
                        currents.append(points.get(False))
                        currents = currents[1:]
                    except queue.Empty:
                        time.sleep(self.timeout['points'])

                next_point = None
                while next_point == None:
                    try:
                        next_point = points.get(False)
                    except queue.Empty:
                        time.sleep(self.timeout['points'])

                if next_point > self.threshold['bot']:
                    bits.put(0)
                    bits.put(0)
                    currents = [currents[-1]]
                    break

            print("")

            last_bits = []
            while 1:
                if len(currents) == frame_size:
                    bit = int(ultranet.get_bit(currents, frame_size) > self.threshold['bot'])
                    currents = []
                    bits.put(bit)
                    last_bits.append(bit)

                if len(last_bits) == self.timeout['different_bit_boundary']:
                    if sum(last_bits) == 0:
                        break
                    last_bits = last_bits[1:]

                try:
                    currents.append(self.points.get(False))
                except queue.empty:
                    time.sleep(self.timeout['points'])

    def bits_processing(self):
        while True:
            currents = []
            while len(currents) < 2 or currents[-len(self.sigil):len(currents)] != self.sigil:
                try:
                    currents.append(self.bits.get(False))
                except queue.Empty:
                    time.sleep(self.timeout['bits'])

            sys.stdout.write(osi1.decode(currents[:-len(sigil)]))
            sys.stdout.flush()

    def callback(self, input, n_frame, time_status, status):
        frames = list(ultranet.chunks(ultranet.unpack(input), self.chunk))
        for frame in frames:
            if not self.input_frames.full():
                self.input_frames.put(frame, False)

        return input, pyaudio.paContinue

    def start_stream_analysis(self):

        p = pyaudio.PyAudio()
        stream = p.open(format=self.format,
                        channels=setup.channels,
                        rate=setup.rate,
                        input=True,
                        frames_per_buffer=self.frames_pbuffer,
                        stream_callback=self.callback
                        )
        stream.start_stream()
        while stream.is_active():
            time.sleep(self.timeout['sample'])




