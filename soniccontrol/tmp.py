import serial
import time
from datetime import datetime
import random
import os
import sys

import tkinter as tk
import tkinter.ttk as ttk

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style

def timestamp():
    return str(datetime.fromtimestamp(int(time.time)))

def animate(i):
    filehandle = open(datafile_name, "r")
    pulldata = filehandle.read()
    
    datalist = pulldata.split('\n')
    x_list = []
    y_list = []
    i = 0
    

on
startloop 3
setMHz
frequency 1000000
gain 100
startloop 2
ramp 2100000,1900000,10000,100
endloop
hold 10
endloop
off