from class_Listener import Listener
import setup
import pyaudio
import sys


frame_size  = setup.frame_size
chunk       = setup.chunk
listen_freq = setup.listen_freq
rate        = setup.rate
sigil_opts  = [int(o) for o in setup.sigil_opts]
input_size  = 4000
format=pyaudio.paInt16
threshold   = {'bot':8000, 'up':None}



listener = Listener(frame_size, chunk, listen_freq, rate, sigil_opts, input_size, format=format, threshold=threshold)
sys.stdout.write("Listening at {}Hz".format(listen_freq))
sys.stdout.flush()
listener.start_stream_analysis()
