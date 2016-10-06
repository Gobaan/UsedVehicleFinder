import matplotlib.pyplot as plt
import numpy as np

def pickPoint(data):
    """Displays a 2D array on the screen and prints data info based upon user clicks."""

    def pickPointSelectVal(event):
        if event.button == 3:
            fig.canvas.mpl_disconnect(cid)
            plt.close(fig)
        else:
            print 'got click: ', event.x, ',', event.y, ' value: ', data[event.x,event.y]

    dims = data.shape
    dpi = 96.0
    fdims = (x/dpi for x in dims)

    fig = plt.figure(figsize=fdims, dpi=dpi)
    plt.figimage(data.transpose(),origin='lower',cmap='gray')
    cid = fig.canvas.mpl_connect('button_press_event', pickPointSelectVal)
    display(fig)

if __name__ == "__main__":
    a = np.arange(500)
    b = np.reshape(np.repeat(a,100),(500,100))
    c = b * np.reshape(np.repeat(np.arange(100),500),(100,500)).transpose()
    pickPoint(c)

