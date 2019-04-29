import matplotlib

matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import RPi.GPIO as GPIO
import numpy as np
from scipy.io import wavfile
import time
import os.path
import Speaker
from FileSettings import SPEAKER_FILE

filename = SPEAKER_FILE

# setup pins
upPin = 23
downPin = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(upPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(downPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# initialize matplot figure  
plt.ion()
plt.style.use('dark_background')
fig = plt.figure()

while True:
    # check if current audio file exists 
    if os.path.isfile(filename) == True:
        # create sound object with the desired audio file
        mySound = Speaker.Speaker(filename)
        # collect frames/second and sound pressure data from .wav file
        fs, data = wavfile.read(filename)
        # time for each iteration (display update)
        tRefresh = 0.085
        # how much data to plot per sec to match the sampling speed
        dataPerFrame = int(fs * tRefresh)
        # declare first band of data
        dataLow = 0
        dataHigh = dataPerFrame
        # set the incriment 
        n = dataPerFrame
        data = np.append(data, [0 for x in range(len(data) % dataPerFrame)])
        # create Axes
        ax = fig.add_subplot(111)
        ax.spines['bottom'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.get_xaxis().set_visible(False)

        # set the y-axis min and max with the max value from the data
        maxData = np.amax(data)
        ax.set_ylim(-maxData, maxData)

        # plot the first set of data
        line, = ax.plot(data[dataLow:dataHigh])
        fig.canvas.draw()

        # start clock and play sound 
        ti = time.time()
        mySound.play()

        # check if either button is pushed and turn the volume up or down
        while dataHigh < len(data) - n:
            if GPIO.input(upPin) == True:
                mySound.volumeUp()
            elif GPIO.input(downPin) == True:
                mySound.volumeDown()
            # incriment the data
            dataLow += n
            dataHigh += n
            # chenage the ydata of the Axes and redraw the figure 
            line.set_ydata(data[dataLow:dataHigh])
            ax.draw_artist(ax.patch)
            ax.draw_artist(line)
            fig.canvas.update()
            fig.canvas.flush_events()

            # check if the time during the iteration is less than 'trefresh'
            # idle if less than 
            while (time.time() - ti) < tRefresh:
                pass
            # reset clock 
            ti = time.time()

    else:
        pass
