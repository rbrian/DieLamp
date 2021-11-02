import time
import digitalio
import board
from rainbowio import colorwheel
import neopixel
import busio
import adafruit_lis3dh
import random
import audiomp3
import audiopwmio
from fns import functions
#import datetime

NUM_PIXELS = 2  # NeoPixel strip length (in pixels)

funcs = functions(NUM_PIXELS)

enable = digitalio.DigitalInOut(board.D10)
enable.direction = digitalio.Direction.OUTPUT
enable.value = True

# Set up accelerometer on I2C bus, 4G range:
i2c = busio.I2C(board.SCL, board.SDA)
int1 = digitalio.DigitalInOut(board.D6)
accel = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1)
accel.range = adafruit_lis3dh.RANGE_4_G
accel.set_tap(1, 100)

statePulse = 0
stateTwinkle = 1
stateShaken1 = 2
stateShaken2 = 3

runmode = 2
# 0 = white red green twinkle
# 1 = white twinkle
# 2 = rainbow twinkle

for x in range(NUM_PIXELS):
    funcs.setRandomMode(0, x)
    funcs.setRandomMode(2, x)

funcs.initMode(runmode)

state = stateTwinkle
funcs.initTwinkle(0)

while True:
    #print(datetime.time())
    #print(funcs.nextTwinkle)

    if state != stateShaken1 and state != stateShaken2 and accel.shake(shake_threshold=10):
        lastState = state
        print("Shaken!")
        funcs.strip.fill((0,0,0,0))
        funcs.strip.show()
        state = stateShaken1
        funcs.playmp3("sounds\dieshake.mp3")
    if state == stateShaken1:
        if funcs.audio.playing:
            funcs.lightRandom()
            time.sleep(0.025)
        else:
            nextsleep = 0.05
            state = stateShaken2
            funcs.playmp3("sounds\dieroll.mp3")
    elif state == stateShaken2:
        if funcs.audio.playing:
            funcs.lightRandom()
            time.sleep(nextsleep)
            nextsleep *= 1.25
            print(nextsleep)
            outtime = time.time() + 30
        else:
            funcs.strip[funcs.laston] = (0,0,0,255);
            if time.time() > outtime:
                print("time out")
                state = lastState

            x, y, z = accel.acceleration
            if accel.tapped:
                print("tap out")
                state = lastState
    elif state == stateTwinkle:
        x, y, z = accel.acceleration
        # print(x, y, z)
        # time.sleep(0.1)
        if accel.tapped:
            print("Tapped!")
            runmode += 1
            if runmode <= 2:
                funcs.initTwinkle(runmode)
            else:
                runmode = 0
                funcs.initMode(runmode)
        if time.time() > funcs.nextTwinkle:
            pix = random.randint(0,NUM_PIXELS-1)
            while funcs.twinkleTimes[pix] != 0:
                pix = random.randint(0,NUM_PIXELS-1)
            print(pix)
            funcs.strip[pix] = funcs.getRandomPixel(runmode)
            funcs.twinkleTimes[pix] = time.time() + 1
            funcs.nextTwinkle = funcs.nextTwinkle + 2

        print (time.time(), funcs.twinkleTimes)
        for x in range(NUM_PIXELS):
            if funcs.twinkleTimes[x] < time.time():
                funcs.strip[x] = funcs.pale
                funcs.twinkleTimes[x] = 0
        print (funcs.twinkleTimes)
        funcs.strip.show()

    elif state == statePulse:
        x, y, z = accel.acceleration
        # print(x, y, z)
        # time.sleep(0.1)
        if accel.tapped:
            print("Tapped!")
            runmode += 1
            if runmode > 2:
                runmode = 0;
                state = stateTwinkle
                funcs.initTwinkle(runmode)
                continue
            funcs.initMode(runmode)

        for x in range(NUM_PIXELS):
            #    print(curMode[x])
            #    print(curModeInc[x])
            newX = funcs.addPix(funcs.curMode[x], funcs.curModeInc[x])
            if funcs.gtPix(newX, funcs.mode[runmode][x]):
                funcs.curModeInc[x] = funcs.multPix(funcs.curModeInc[x], -1)
                funcs.curMode[x] = funcs.addPix(funcs.curMode[x], funcs.curModeInc[x])
            elif funcs.ltPix(newX):
                funcs.setRandomMode(runmode, x)
                funcs.curMode[x] = (0, 0, 0, 0)
                funcs.curModeInc[x] = funcs.modeStep[runmode][x]
            else:
                funcs.curMode[x] = newX
            funcs.strip[x] = funcs.curMode[x]
        funcs.strip.show()
