from machine import I2S, Pin
import time, struct

BCK_PIN = 32
WS_PIN = 25
SD_LEFT = 33
SD_RIGHT = 12
SAMPLE_RATE = 16000
SAMPLES = 32

i2s_left = I2S(
    0,
    sck=Pin(BCK_PIN),
    ws=Pin(WS_PIN),
    sd=Pin(SD_LEFT),
    mode=I2S.RX,
    bits=32,
    format=I2S.STEREO,
    rate=SAMPLE_RATE,
    ibuf=4 * SAMPLES
)

i2s_right = I2S(
    1,
    sck=Pin(BCK_PIN),
    ws=Pin(WS_PIN),
    sd=Pin(SD_RIGHT),
    mode=I2S.RX,
    bits=32,
    format=I2S.STEREO,
    rate=SAMPLE_RATE,
    ibuf=4 * SAMPLES
)

buf_left = bytearray(SAMPLES * 4)
buf_right = bytearray(SAMPLES * 4)

while True:
    i2s_left.readinto(buf_left)
    i2s_right.readinto(buf_right)
    left = struct.unpack_from("<" + "i" * (SAMPLES), buf_left)
    right = struct.unpack_from("<" + "i" * (SAMPLES), buf_right)

    amp_l = sum(abs(s >> 14) for s in left) // len(left)
    amp_r = sum(abs(s >> 14) for s in right) // len(right)

    amp_l = max(amp_l, 0)
    amp_r = max(amp_r, 0)


    print("L:{:4d}  R:{:4d}".format(amp_l, amp_r))
