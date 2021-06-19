import pyaudio
import math
import struct
import wave
import time
import os
import http.client
import urllib

Threshold = 150

SHORT_NORMALIZE = (1.0/32768.0)
chunk = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
swidth = 2

class Recorder:

    @staticmethod
    def rms(frame):
        count = len(frame) / swidth
        format = "%dh" % (count)
        shorts = struct.unpack(format, frame)

        sum_squares = 0.0
        for sample in shorts:
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n
        rms = math.pow(sum_squares / count, 0.5)

        return rms * 1000

    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  frames_per_buffer=chunk)

    def sendpush(self):
        print('Noise detected, sending push message')
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
          urllib.parse.urlencode({
            "token": "XXXXXX",
            "user": "XXXXXX",
            "message": "Crying Baby detected!",
          }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()
        print('Waiting for 10 Seconds')
        self.stream.stop_stream()
        time.sleep(10)
        print('Returning to Listening-Mode')
        self.stream.start_stream()

    def listen(self):
        print('Starting Listening-Mode')
        while True:
            input = self.stream.read(chunk)
            rms_val = self.rms(input)
            if rms_val > Threshold:
                self.sendpush()

a = Recorder()
a.listen()