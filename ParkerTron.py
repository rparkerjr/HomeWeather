import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import requests
import tkinter as tk
from tkinter import font as tkfont

import OpenWeather as W

%matplotlib inline

main = tk.Tk()
main.title('ParkerTron')

width = main.winfo_screenwidth()
height = main.winfo_screenheight()
#main.geometry('800x480') # this should adjust to actual screen size
main.resizable(False, False)

canvas = tk.Canvas(master = main, width = width, height = height, bg = 'black')
canvas.pack()

myWeather = W.OpenWeather(W.api_key, W.city, W.latlong)
myWeather.refresh_onecall()
temperature = myWeather.current.temp[0]

field = tk.Frame(master = main, bg = 'yellow')
field.place(relx = 0.26, rely = 0.05, relwidth = 0.73, relheight = 0.9)
temperature = tk.Label(master = field,
	bg = 'black', fg = 'white', 
	text = temperature, font = 'Helvetica, 72', 
	wraplength = 555)

main.mainloop()