from __future__ import print_function
from collections import Counter, deque
import _thread #python2
import sys
import numpy as np

# append local directory './myo_raw' (containing python myo apis) to the path
sys.path.append('./myo_raw/')       
from myo_raw import MyoRaw          # myo APIs

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

import scipy.io as sio  #Save as .mat files

import time
from datetime import date

import xml.etree.ElementTree as ET  # Read xml files

#GUI Interface
import tkinter
from tkinter.ttk import Labelframe
from PIL import Image, ImageTk

#pyqtgraph.examples.run()

# -----------------------------------------------
# Global variables
# -----------------------------------------------
BUFFER_SIZE = 1000

myo = 0
myo_initialized = False

time0 = 0
time_previous = 0
time_next = 0

emg_data_buffer = np.zeros((BUFFER_SIZE, 8))
emg_data_latest = np.zeros((1, 8))
quat_data_buffer = np.zeros((BUFFER_SIZE, 4))
quat_data_latest = np.zeros((1, 4))
acc_data_buffer = np.zeros((BUFFER_SIZE, 3))
acc_data_latest = np.zeros((1, 3))
gyro_data_buffer = np.zeros((BUFFER_SIZE, 3))
gyro_data_latest = np.zeros((1, 3))

# Final arrays for EMG, accelerometer, gyroscope, and time
emg_tot = np.array([[0, 0, 0, 0, 0, 0, 0, 0]])
quat_tot = np.array([[0, 0, 0, 0]])
acc_tot = np.array([[0, 0, 0]])
gyro_tot = np.array([[0, 0, 0]])
time_tot = np.array([0])

terminate_program = False
thread_ended = False
plot_graph = False
set_up = False

# Date, patient data
cdate = 0
pat_name = '0'
pat_age = '0'
arm = '0'

# Conditions : can be set in parameters.xml
condition = np.array([0])
instructions = np.array([["0", 0, 0, 0, 0]])
nb_trials = 0
trial_vector = np.array([0])


# -----------------------------------------------
# myo thread
# -----------------------------------------------
def thread_myo():
    global emg_data_buffer, emg_data_latest, quat_data_latest, \
           quat_data_buffer, acc_data_latest, acc_data_buffer, gyro_data_latest, \
           gyro_data_buffer
    global thread_ended
    global emg_tot, quat_tot, acc_tot, gyro_tot
    global time0, time_tot, time_previous, time_next
    global condition, instructions, nb_trials, set_up, trial_vector

    # run loop
    print('Myo thread started.')
    instr = instructions
    time_previous = 0

    while True:
        # check if thread has to be terminated
        global terminate_program
        if terminate_program:
            print('Myo thread terminated.')
            thread_ended = True
            _thread.exit_thread()    

        myo.run()

        # update buffers
        emg_data_buffer = np.roll(emg_data_buffer,-1,0)
        emg_data_buffer[-1] = emg_data_latest

        quat_data_buffer = np.roll(quat_data_buffer,-1,0)
        quat_data_buffer[-1] = quat_data_latest

        acc_data_buffer = np.roll(acc_data_buffer,-1,0)
        acc_data_buffer[-1] = acc_data_latest

        gyro_data_buffer = np.roll(gyro_data_buffer,-1,0)
        gyro_data_buffer[-1] = gyro_data_latest
               
        def buildtotal (array_latest, array_tot, size):
            provisoire = np.asarray(array_latest)
            if provisoire.shape == (size,):
                provisoire = np.expand_dims(provisoire, axis=1)
                provisoire = np.transpose(provisoire)
    
            array_tot = np.concatenate((array_tot, provisoire), axis=0)
            return array_tot
        
        
        
        if not set_up:
            time_next = time_previous + instr[0, 2]*1000
            #get current time in milliseconds.
            time_prov = time.time() * 1000 - time0
            # Build the final arrays (to be saved in .mat)
            time_tot = np.append(time_tot, [time_prov], axis=0)
            
            emg_tot = buildtotal(emg_data_latest, emg_tot, 8)
            quat_tot = buildtotal(quat_data_latest, quat_tot, 4)
            acc_tot = buildtotal(acc_data_latest, acc_tot, 3)
            gyro_tot = buildtotal(gyro_data_latest, gyro_tot, 3)
            
            #build the array of the conditions with randomized conditions. 
            # There is always a rest step between 2 conditions.

            # add 1 open and 1 close in the beginning because errors in the EMG
            if time_prov >= 0 and time_prov < 1000:#wait one second before starting
                condition = np.append(condition, [condition[-1]], axis=0)
                trial_vector = np.append(trial_vector, [trial_vector[-1]], axis=0)

            elif 1000 <= time_prov and time_prov <= 2*instructions[0,2]*1000 + instructions[1,2]*1000 :
                if time_prov <= time_next :
                    condition = np.append(condition, [condition[-1]], axis=0)
                    trial_vector = np.append(trial_vector, [trial_vector[-1]], axis=0)
                else :
                    if condition[-1] == 0 : #if previous condition was Rest
                        n = np.random.randint(1, 2)
                        condition = np.append(condition, [instr[n, 1]], axis=0)
                        time_previous = time_next
                        time_next = time_previous + instr[n, 2] * 1000
                        nb_trials = nb_trials - 1
                        trial_vector = np.append(trial_vector, [trial_vector[-1] + 1], axis=0)

                    else : # if previous condition was open/close/...
                        condition = np.append(condition, [instr[0, 1]], axis=0)     
                        time_previous = time_next
                        time_next = time_previous + instr[0, 2] * 1000
                        trial_vector = np.append(trial_vector, [trial_vector[-1]], axis=0)

            elif time_prov <= time_next :
                condition = np.append(condition, [condition[-1]], axis=0)
                trial_vector = np.append(trial_vector, [trial_vector[-1]], axis=0)
            
            else :
                if condition[-1] == 0 : #if previous condition was Rest
                    n = np.random.randint(1, instr.shape[0])
                    condition = np.append(condition, [instr[n, 1]], axis=0)
                    instr[n, 3] -= 1
                    time_previous = time_next
                    time_next = time_previous + instr[n, 2] * 1000
                    nb_trials = nb_trials - 1
                    trial_vector = np.append(trial_vector, [trial_vector[-1] + 1], axis=0)
                    if instr[n, 3] == 0:
                        instr = np.delete(instr, n, 0)
                    
                else :
                    condition = np.append(condition, [instr[0, 1]], axis=0)     
                    time_previous = time_next
                    time_next = time_previous + instr[0, 2] * 1000
                    trial_vector = np.append(trial_vector, [trial_vector[-1]], axis=0)

                    if instr.shape[0] == 1:
                        terminate_program = True
    

# -----------------------------------------------
# cleanup
# -----------------------------------------------
def cleanup(argument):
    # terminate myo thread
    global terminate_program
    terminate_program = True

    # disconnect myo
    global myo_initialized
    if (myo_initialized):
        myo.disconnect()
        print('Myo disconnected')


# -----------------------------------------------
# set-up myo
# -----------------------------------------------
def setup_myo():
    global myo, myo_initialized
    
    print('Setting up myo ...')
    
    myo = MyoRaw(None)

    def emg_handler(emg, moving, times=[]):
        # store data
        global emg_data_latest
        emg_data_latest = emg

    def imu_handler(quat, acc, gyro):
        # store data
        global quat_data_latest, acc_data_latest, gyro_data_latest
        quat_data_latest = quat
        acc_data_latest = acc
        gyro_data_latest = gyro

    myo.add_emg_handler(emg_handler)
    myo.add_imu_handler(imu_handler)
    myo.connect()
    myo_initialized = True
    print('Myo connected')


    _thread.start_new_thread(thread_myo, ())
    print('Myo setup.\n')

# -----------------------------------------------
# Plot graphs
# -----------------------------------------------
def plot_graphs():
    # init window
    app = QtGui.QApplication([])

    print('Starting up plots and QT ...')

    win = pg.GraphicsWindow(title="Myo data")
    win.resize(1000,1000)
    win.setWindowTitle('Myo data')
    # pg.setConfigOptions(antialias=True) # Enable antialiasing for prettier plots
    pg.setConfigOption('background', 'k')
    pg.setConfigOption('foreground', 'w')

    colors = ['r', 'g', 'b', 'c', 'm', 'y', 'w', 'r'] 
    p_emg = [None] * 8
    emg = [None] * 8

    for i, color in enumerate(colors):
        p_emg[i] = win.addPlot(title="EMG " + str(i + 1))
        p_emg[i].setXRange(0,BUFFER_SIZE)
        p_emg[i].setYRange(-150, 150)
        p_emg[i].enableAutoRange('xy', False)
        emg[i] = p_emg[i].plot(pen=color, name="emg" + str(i + 1))
        win.nextRow()

    def update():
        global emg_data_buffer
        for i in range(8):
            emg[i].setData(emg_data_buffer[1:BUFFER_SIZE,i])

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(10)
   
    print('Plots set up.\n')

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
        

# -----------------------------------------------
#  Read xml file
# -----------------------------------------------
def read_xml():
    global instructions, nb_trials

    root = ET.parse('parameters.xml').getroot()

    for condi in root.findall('conditions/cond'):
        ins = [[condi.get('instruction'), int(condi.get('label')), 
                float(condi.get('duration')), int(condi.get('trials')), 
                condi.get('filename')]]
        instructions = np.vstack((instructions, np.asarray(ins, object)))
        nb_trials = nb_trials + int(condi.get('trials'))
    instructions = np.delete(instructions, 0, axis=0)
    nb_trials = nb_trials + 1
# -----------------------------------------------
# Save to matlab file
# -----------------------------------------------
def save_file():
    global emg_tot, quat_tot, acc_tot, gyro_tot, time_tot
    global cdate, pat_name, pat_age, arm
    global condition, trial_vector
    
    # get the date
    today = date.today()
    cdate = today.strftime("%Y%m%d")
    
    # transpose time and condition to get column vectors
    time_tot = time_tot [:, np.newaxis]
    condition = condition [:, np.newaxis]
    
    # create dictionary
    dico = {}
    # add to dictionary with dico['name'] = variable 
    dico['emg'] = emg_tot
    dico['quat'] = quat_tot
    dico['acc'] = acc_tot
    dico['gyro'] = gyro_tot
    dico['age'] = pat_age
    dico['name'] = pat_name
    dico['time'] = time_tot
    dico['condition'] = condition
    dico['date'] = cdate
    dico['trial_vector'] = trial_vector
    
    if arm.get == 1 :
        dico['arm'] = 'left'
    else :
        dico['arm'] = 'right'
        
    sio.savemat('%s.mat' %(pat_name), dico)
    

# -----------------------------------------------
# GUI window for Patient data
# -----------------------------------------------
def GUIwindow_data ():
    
    global arm
    window = tkinter.Tk()
    window.title("Patient's data")

    #-----Patient data
    patient_data = Labelframe(window, borderwidth=1, text='Patient Data')
    patient_data.grid(row=0, column=0, sticky='NW')
    
    # Patient name
    pat_namelbl = tkinter.Label(patient_data, text="Name")
    pat_namelbl.grid(sticky='NW')
    var_name = tkinter.StringVar()
    patient_name= tkinter.Entry(patient_data, textvariable=var_name)
    patient_name.grid(sticky='NW')
    
    # Patient age
    pat_agelbl = tkinter.Label(patient_data, text="Age")
    pat_agelbl.grid(sticky='W')
    var_age = tkinter.StringVar()
    patient_age = tkinter.Entry(patient_data, textvariable=var_age)
    patient_age.grid(sticky='W')
    
 
    #Radiobutton for left or right arm
    arm = tkinter.IntVar()
    armlbl = tkinter.Label(patient_data, text="Which arm is being studied ?")
    armlbl.grid(sticky='W')
    tkinter.Radiobutton(patient_data, text="Left arm", variable=arm, value=1).grid(sticky='W')
    tkinter.Radiobutton(patient_data, text="Right arm", variable=arm, value=2).grid(sticky='W')
    
    def win_des():
        global pat_name, pat_age
        pat_name = patient_name.get()
        pat_age = patient_age.get()
        window.destroy()
    
    # buttons exit and OK
    btn_exit = tkinter.Button(window, text="Exit", command=sys.exit, fg='red')
    btn_exit.grid(row=2, column=0, sticky='sw')    

    btn_ok = tkinter.Button(window, text="OK", command=win_des)
    btn_ok.grid(row=2, column=2, sticky='se')

    window.mainloop()
    
# -----------------------------------------------
# GUI window for Instructions
# -----------------------------------------------
def GUIwindow_instr ():
    
    global time_tot, instructions, nb_trials
    window = tkinter.Tk()
    window.geometry("500x600") 
    window.title("Instructions")

    message = tkinter.StringVar()
    remaining_trials = tkinter.StringVar()

    img = [Image.open(instructions[0, 4])]
    
    #create an array of all the photos
    for i in range (1, instructions.shape[0]):
        img.append(Image.open(instructions[i, 4]))
    
    #resize the photos
    for i in range (0, instructions.shape[0]):
        img[i] = ImageTk.PhotoImage(img[i].resize((250, 480)))

    panel = tkinter.Label(window, image=img[0])
    panel.grid (row=0, column=1)

    def update():
        global instructions, condition, nb_trials
        
        for i in range (0, instructions.shape[0]):
            if condition[-1] == instructions[i, 1]:
                msg = instructions[i,0]
                message.set(msg) 
                photo = img[i]

        panel.configure(image = photo)
        panel.image = photo
        remaining_trials.set("Remaining trials : " + str(nb_trials))
        window.after(300, update)
    
    tkinter.Label(window, textvariable=message).grid(row=1, column=1)
    tkinter.Label(window, textvariable=remaining_trials).grid(row=2, column=1)
    
    def quitprog ():
        global terminate_program
        terminate_program = True
        window.quit()    
    
    window.columnconfigure(1, weight=1)
    window.rowconfigure(0, weight=1)

    # buttons exit and save
    btn_exit = tkinter.Button(window, text="Exit", command=sys.exit, fg='red')
    btn_exit.grid(row=2, column=0, sticky='sw')    

    btn_save = tkinter.Button(window, text="Save", command=quitprog)
    btn_save.grid(row=2, column=2, sticky='e')
    
    window.after(300, update)
    window.mainloop()


# -----------------------------------------------
# main
# -----------------------------------------------
def main(argv):
    import subprocess
    global plot_graph, thread_ended, set_up, time0
    set_up = True
    read_xml()
    setup_myo()
    plot_graphs()
    
    GUIwindow_data()
    set_up = False
    time0 = time.time()*1000    # Time is in milliseconds
    GUIwindow_instr()
    while not thread_ended:
        pass

    save_file()

# -----------------------------------------------
# entry point
# -----------------------------------------------
# main (used for handling keyboard interrupts)
if __name__ == '__main__':
    try:
        main(sys.argv[1:])

    except KeyboardInterrupt:
        print('Catched keyboard interrupt\n')
        cleanup(1)
        sys.exit(0)
