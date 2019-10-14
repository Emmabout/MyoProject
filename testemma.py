# global variables
from random import randint

import tkinter
from tkinter.ttk import Labelframe

import matplotlib
import numpy as np
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
import matplotlib.backends.tkagg as tkagg  # import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from PIL import Image

# global variables
BUFFER_SIZE = 1000
emg_data_buffer = np.zeros((BUFFER_SIZE, 8))
emg_data_latest = np.zeros((1, 8))
quat_data_buffer = np.zeros((BUFFER_SIZE, 4))
quat_data_latest = np.zeros((1, 4))
acc_data_buffer = np.zeros((BUFFER_SIZE, 3))
acc_data_latest = np.zeros((1, 3))
gyro_data_buffer = np.zeros((BUFFER_SIZE, 3))
gyro_data_latest = np.zeros((1, 3))
save_to_file = False
terminate_program = False
plot_graph = False
time = [0, 1, 2, 3]


def main():
    global emg_data_latest
    global quat_data_latest
    global acc_data_latest
    global gyro_data_latest

    simulated = 1  # input("Simulated ? 1=yes \n")

    if simulated:
        #  generate random data
        emg_data_latest = np.random.randint(0, 2048, size=(4, 8))
        quat_data_latest = np.random.randint(0, 2048, size=(1, 4))
        acc_data_latest = np.random.randint(0, 2048, size=(1, 3))
        gyro_data_latest = np.random.randint(0, 2048, size=(1, 3))


    def save_file():
        filename = pat_name.get() + ".txt"
        np.savetxt(filename, emg_data_latest, newline=',', header='EMG data\nEMG_1 EMG_2 EMG_3 EMG_4 EMG_5 EMG_6 EMG_7 '
                                                                  'EMG_8\n')

    
    def draw_figure(canvas, figure, loc=(0, 0)):
        # Draw a matplotlib figure onto a Tk canvas
        figure_canvas_agg = FigureCanvasAgg(figure)
        figure_canvas_agg.draw()
        figure_x, figure_y, figure_w, figure_h = figure.bbox.bounds
        figure_w, figure_h = int(figure_w), int(figure_h)
        photo = tkinter.PhotoImage(master=canvas, width=figure_w, height=figure_h)

        # Position: convert from top-left anchor to center anchor
        canvas.create_image(figure_w/2, figure_h/2, image=photo)

        # Unfortunately, there's no accessor for the pointer to the native renderer
        tkagg.blit(photo, figure_canvas_agg.get_renderer()._renderer, colormode=2)

        # Return a handle which contains a reference to the photo object
        # which must be kept live or else the picture disappears
        return photo

    # GUI    
    window = tkinter.Tk()
    
    
    # plot
    figure = plt.figure('EMG signals')
    ax = figure.add_subplot(1, 1, 1)
    for i in range(8):
        ax.plot(time, emg_data_latest[:, i], label='EMG' + str(i + 1))
    leg = ax.legend()
    ax.legend(loc='upper left')
    ax.set_xlabel('Time')
    ax.set_ylabel('EMG')
    # plt.show()
    figure_x, figure_y, figure_w, figure_h = figure.bbox.bounds
    
    # Enter patient data (name)
    patient_data = Labelframe(window, borderwidth=1, text='Patient Data')
    patient_data.grid(row=0, column=0, sticky='NW')
    pat_label = tkinter.Label(patient_data, text="Name")
    pat_label.grid(sticky='NW')
    var_text = tkinter.StringVar()
    pat_name = tkinter.Entry(patient_data, textvariable=var_text)
    pat_name.grid(sticky='NW')
    
    

    # Maybe show graphs of the EMG ?
    graphs_emg = Labelframe(window, borderwidth=1, text='EMG signals')
    graphs_emg.grid(row=0, column=1, sticky='E')
    canvas = tkinter.Canvas(graphs_emg, width=figure_w, height=figure_h)
    canvas.grid(sticky='E')
    
    listbox = tkinter.Listbox(window)
    listbox.grid(row=0, column=2)
    
    listbox.insert(0, "entry")
    for item in ["one", "two", "three", "four"]:
        listbox.insert(0, item)
    
    # Image.resize()
    figure_photo = draw_figure(canvas, figure, loc=(figure_x, figure_y))


    # buttons exit and save
    btn_exit = tkinter.Button(window, text="Exit", command=window.quit, fg='red')
    btn_exit.grid(row=2, column=0, sticky='sw')    
    btn_stop = tkinter.Button(window, text="Stop")
    btn_stop.grid(row=2, column=1, sticky='sw')
    btn_save = tkinter.Button(window, text="Save", command=save_file)
    btn_save.grid(row=2, column=2, sticky='se')
    
    window.mainloop()


main()
