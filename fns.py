import time
import board
import digitalio
import random
import audiomp3
import audiopwmio
import neopixel

class functions:

    laston = -1

    def __init__(self, numPixels):
        self.strip = neopixel.NeoPixel(
            board.D5, numPixels, brightness=0.4, auto_write=False, pixel_order=neopixel.GRBW
        )
        self.audio = audiopwmio.PWMAudioOut(board.A0)
        self.numPixels = numPixels
        self.modeSteps = 10
        self.mode = (self.createList(), self.createList((0, 0, 0, 255)), self.createList())
        self.modeStep = (self.createList(), self.createList((0, 0, 0, 255 // self.modeSteps)), self.createList())
        self.curMode = self.createList()
        self.curModeInc = self.createList()


    def gtPix(self, t, u):
        return (t[0] > u[0]) or (t[1] > u[1]) or (t[2] > u[2]) or (t[3] > u[3])


    def ltPix(self, t):
        return t[0] < 0 or t[1] < 0 or t[2] < 0 or t[3] < 0


    def createList(self, value=(0, 0, 0, 0)):
        list = [value]
        for x in range(self.numPixels - 1):
            list.append(value)
        return list

    def addPix(self, p1, p2):
        return (p1[0] + p2[0], p1[1] + p2[1], p1[2] + p2[2], p1[3] + p2[3])


    def multPix(self, p1, n):
        return (p1[0] * n, p1[1] * n, p1[2] * n, p1[3] * n)


    def setMode(self, n, x, t):
        self.mode[n][x] = t
        self.modeStep[n][x] = (
            t[0] // self.modeSteps,
            t[1] // self.modeSteps,
            t[2] // self.modeSteps,
            t[3] // self.modeSteps,
        )


    def randomPixel(self):
        newmode = (0, 0, 0, 0)
        while newmode == (0, 0, 0, 0):
            newmode = (
                random.randint(0, 1) * 255,
                random.randint(0, 1) * 255,
                random.randint(0, 1) * 255,
                0,
            )
        return newmode

    def getRandomPixel(self, n):
        if n == 0:
            v = random.randint(0, 2)
            if v == 0:
                return (0, 0, 0, 255)
            elif v == 1:
                return (255, 0, 0, 0)
            else:
                return (0, 255, 0, 0)
        elif n == 1:
            return (0, 0, 0, 255)
        else:  # n==2
            return self.randomPixel()

    def setRandomMode(self, n, x):
        self.setMode(n,x, self.getRandomPixel(n))

    def initModeX(self, n, x):
        self.curMode[x] = self.multPix(self.modeStep[n][x], random.randint(0, self.modeSteps))
        if random.randint(0, 1) == 0:
            self.curModeInc[x] = self.multPix(self.modeStep[n][x], -1)
        else:
            self.curModeInc[x] = self.modeStep[n][x]


    def initMode(self, n):
        for x in range(self.numPixels):
            self.initModeX(n, x)


    def playmp3(self, file):
        decoder = audiomp3.MP3Decoder(open(file, "rb"))
        self.audio.play(decoder)

    def lightRandom(self):
        if self.laston != -1:
            self.strip[self.laston] = (0, 0, 0, 0)
        self.laston = random.randint(0, self.numPixels - 1)
        self.strip[self.laston] = self.randomPixel()
        self.strip.show()

    pale = (0,0,0,32)

    def initTwinkle(self,n):
        print("initT")
        self.twinklemode = n
        self.nextTwinkle = time.time() + 2
        self.twinkleTimes = self.createList(0)
        self.strip.fill(self.pale)
