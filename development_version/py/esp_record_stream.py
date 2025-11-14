import network
import socket
from machine import I2S, Pin
import struct
import time

# -------------------------
# WiFi Setup
# -------------------------
SSID = "3rd_Floor"
PASS = "spit@123"

w = network.WLAN(network.STA_IF)
w.active(True)
w.connect(SSID, PASS)
while not w.isconnected():
    time.sleep(0.2)
print("Connected:", w.ifconfig())

# -------------------------
# I2S Configuration
# -------------------------
SAMPLE_RATE = 16000
BITS = 32
FRAME_SAMPLES = 128   # number of samples per channel per frame

i2s0 = I2S(
    0,
    sck=Pin(32),
    ws=Pin(25),
    sd=Pin(33),
    mode=I2S.RX,
    bits=BITS,
    format=I2S.STEREO,
    rate=SAMPLE_RATE,
    ibuf=4096
)

i2s1 = I2S(
    1,
    sck=Pin(14),
    ws=Pin(12),
    sd=Pin(13),
    mode=I2S.RX,
    bits=BITS,
    format=I2S.STEREO,
    rate=SAMPLE_RATE,
    ibuf=4096
)

buf0 = bytearray(FRAME_SAMPLES * 8)   # stereo => 2 ch * 4 bytes * N samples
buf1 = bytearray(FRAME_SAMPLES * 8)

# -------------------------
# TCP Client Setup
# -------------------------
SERVER_IP = "10.10.30.30"
SERVER_PORT = 5000

sock = socket.socket()
sock.connect((SERVER_IP, SERVER_PORT))
print("Connected to PC")

# -------------------------
# Stream Loop
# -------------------------
while True:
    if i2s0.readinto(buf0) and i2s1.readinto(buf1):
        s0 = struct.unpack("<" + "i"*(len(buf0)//4), buf0)
        s1 = struct.unpack("<" + "i"*(len(buf1)//4), buf1)

        mic1 = s0[0::2]
        mic2 = s0[1::2]
        mic3 = s1[0::2]
        mic4 = s1[1::2]

        # Interleave 4 channels: M1 M2 M3 M4 M1 M2 M3 M4 …
        frame = bytearray()
        for i in range(FRAME_SAMPLES):
            frame += struct.pack(
                "<iiii",
                mic1[i],
                mic2[i],
                mic3[i],
                mic4[i]
                )

        sock.send(frame)
