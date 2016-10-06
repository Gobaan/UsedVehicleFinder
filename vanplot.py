import pandas
import time
import json
import bs4
import requests
import matplotlib.pyplot as plt
from time import gmtime, strftime

with open('vans.jsons', 'r') as fp:
    vans = [json.loads(line) for line in fp]

frame = pandas.DataFrame(vans)
frame['odometer'] = [int(value) for value in frame['odometer']]
frame['price'] = [int(value.replace('$', '')) for value in frame['price']]

def onclick(event):
    print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          (event.button, event.x, event.y, event.xdata, event.ydata))

fig = plt.figure(figsize=(20, 10))
localonly = frame['expanded'] == False
print(sum(localonly))

def color(query):
    if query == "dodge ram van": return "red"
    elif query == "chevy express": return "blue"
    elif query == "gmc savana": return "green"
    elif query == "cargo van": return "magenta"
    elif query == "ford transit": return "purple"
    elif query.startswith("ford"): return "black"
    else: return "yellow"

colors = [color(query) for query in frame[localonly]["query"]]
plot = plt.scatter(frame['odometer'][localonly], frame['price'][localonly], color=colors)

cid = fig.canvas.mpl_connect('button_press_event', onclick)
