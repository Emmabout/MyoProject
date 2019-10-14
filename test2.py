from __future__ import print_function
from collections import Counter, deque
import _thread #python2
#import threading # python3
import sys
import getopt
import time
import numpy as np
#from common import *
sys.path.append('./myo_raw/')       # append local directory './myo_raw' (containing python myo apis) to the path
from myo_raw import MyoRaw          # myo APIs
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import scipy.io as sio
from numpy.core.records import fromarrays
import time
import xml.etree.ElementTree as ET  # to write xml files

#GUI Interface
import tkinter
from tkinter.ttk import Labelframe
from datetime import date

#to put images in GUi window
from PIL import Image, ImageTk

#pyqtgraph.examples.run()

# -----------------------------------------------
# global variables
# -----------------------------------------------
BUFFER_SIZE = 1000
Niteration = 0
file_handle = 0
myo = 0
myo_initialized = False
time0 = 0



emg_data_buffer = np.zeros((BUFFER_SIZE, 8))
emg_data_latest = np.zeros((1, 8))
quat_data_buffer = np.zeros((BUFFER_SIZE, 4))
quat_data_latest = np.zeros((1, 4))
acc_data_buffer = np.zeros((BUFFER_SIZE, 3))
acc_data_latest = np.zeros((1, 3))
gyro_data_buffer = np.zeros((BUFFER_SIZE, 3))
gyro_data_latest = np.zeros((1, 3))

# final arrays 
emg_tot = np.array([[0, 0, 0, 0, 0, 0, 0, 0]])
quat_tot = np.array([[0, 0, 0, 0]])
acc_tot = np.array([[0, 0, 0]])
gyro_tot = np.array([[0, 0, 0]])
time_tot = np.array([0])

terminate_program = False
thread_ended = False
plot_graph = False
#app = QtGui.QApplication([])
app = 0

# date, patient data
cdate = 0
pat_name = '0'
pat_age = '0'

# conditions
condition = np.array([0])  # 0 : rest. 1 : open. 2 : close. 3 : open+exo. 4 : close+exo.

#win = pg.GraphicsWindow(title="Myo data")
#QtGui.QApplication.setGraphicsSystem('raster')
#mw = QtGui.QMainWindow()
#mw.resize(800,800)


# -----------------------------------------------
# myo thread
# -----------------------------------------------
def thread_myo():
    global emg_data_buffer, emg_data_latest, quat_data_latest, quat_data_buffer, acc_data_latest, acc_data_buffer, gyro_data_latest, gyro_data_buffer, simulated
    global Niteration, thread_ended
    global emg_tot, quat_tot, acc_tot, gyro_tot
    global time0, time_tot
    global condition

    # run loop
    print('Myo thread started.')
    # time will be in milliseconds (hence *1000)
    time0 = time.time()*1000

    while True:
        # check if thread has to be terminated
        global terminate_program
        
        if terminate_program:
            print('Myo thread terminated')
            thread_ended = True
            _thread.exit_thread()    

        myo.run()
        
        # update Niterations
        Niteration= Niteration+1

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
        
        #get current time in milliseconds.
        time_prov = time.time() * 1000 - time0
        
        # Build the final arrays (to be saved in .mat)
        time_tot = np.append(time_tot, [time_prov], axis=0)
         
        emg_tot = buildtotal(emg_data_latest, emg_tot, 8)
        quat_tot = buildtotal(quat_data_latest, quat_tot, 4)
        acc_tot = buildtotal(acc_data_latest, acc_tot, 3)
        gyro_tot = buildtotal(gyro_data_latest, gyro_tot, 3)
        
        
        # build the vector condition : if the modulo of time by 10000 is between 0 and 5000ms, the instruction given is rest (0). Else, the condition takes a random value between 1 and 4, iving the instruction for the patient ONLY if the previous value of 'condition' was 0. Else, 'condition' takes its previous value.
        
        if (time_prov % 10000) >= 0 and (time_prov % 10000) <= 5000 :
            condition = np.append(condition, [0], axis=0)     
        else :
            if condition [-1] == 0:
                condition = np.append(condition, [2], axis=0) #np.append(condition, [np.random.randint(1,5)], axis=0)
                
            else :
                condition = np.append(condition, [condition[-1]], axis=0) 


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
    
    #myo = MyoRaw(sys.argv[1] if len(sys.argv) >= 2 else None)
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
    #myo.add_arm_handler(lambda arm, xdir: print('arm', arm, 'xdir', xdir))
    #myo.add_pose_handler(lambda p: print('pose', p))
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
    win.closeEvent = cleanup
    win.resize(1000,1000)
    win.setWindowTitle('Myo data')
    pg.setConfigOption('background', 'k')
    pg.setConfigOption('foreground', 'w')

    ratio = 1.5

    p_emg = win.addPlot(title="EMG")
    p_emg.setXRange(0,BUFFER_SIZE)
    p_emg.setYRange(-2048*7*ratio, 2048)
    p_emg.enableAutoRange('xy', False)    
    
    color = ['r', 'g', 'b', 'c', 'm', 'y', 'w', 'r']
    emg_list = np.empty([8], dtype=pg.PlotDataItem)
    
    for i in range(8):
        emg_list[i] = p_emg.plot(pen=color[i], name="emg" + str(i))
        
    win.nextRow()

    p_quat = win.addPlot(title="QUATERNIONs")
    p_quat.setXRange(0,BUFFER_SIZE)
    p_quat.setYRange(-3000*4*ratio, 3000)
    p_quat.enableAutoRange('xy', False)
    
    
    quat_a = p_quat.plot(pen='r', name="quaternionA")
    quat_b = p_quat.plot(pen='g', name="quaternionB")
    quat_c = p_quat.plot(pen='b', name="quaternionC")
    quat_d = p_quat.plot(pen='w', name="quaternionD")
    
    quat = [quat_a, quat_b, quat_c, quat_d]
    win.nextRow()

    p_acc = win.addPlot(title="ACCELEROMETERs")
    p_acc.setXRange(0,BUFFER_SIZE)
    p_acc.setYRange(-3000*3*ratio, 3000)
    p_acc.enableAutoRange('xy', False)
    acceleration_x = p_acc.plot(pen='r', name="accelerationX")
    acceleration_y = p_acc.plot(pen='g', name="accelerationY")
    acceleration_z = p_acc.plot(pen='b', name="accelerationZ")
    
    acc_list = [acceleration_x, acceleration_y, acceleration_z]
    win.nextRow()

    p_gyro = win.addPlot(title="GYROSCOPEs")
    p_gyro.setXRange(0,BUFFER_SIZE)
    p_gyro.setYRange(-2048*3*ratio, 2048)
    p_gyro.enableAutoRange('xy', False)
    gyro_x = p_gyro.plot(pen='r', name="gyroX")
    gyro_y = p_gyro.plot(pen='g', name="gyroY")
    gyro_z = p_gyro.plot(pen='b', name="gyroZ")
    
    gyro_list = [gyro_x, gyro_y, gyro_z]
    win.nextRow()

    # ---------Update graphs
    def update():
        global emg_data_buffer
        for i in range(8):
            emg_list[i].setData( emg_data_buffer[1:BUFFER_SIZE,i] - i*2048*ratio )

        global quat_data_buffer
        for i in range(4):
            quat[i].setData( quat_data_buffer[1:BUFFER_SIZE,i] - i*3000*ratio )

        global acc_data_buffer
        for i in range(3):
            acc_list[i].setData( acc_data_buffer[1:BUFFER_SIZE,i] - i*3000*ratio )

        global gyro_data_buffer
        for i in range(3):
            gyro_list[i].setData( gyro_data_buffer[1:BUFFER_SIZE,i] - i*2048*ratio )
            
    
    update()        
       
    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(10)

    print('Plots set up.\n')

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
        
        
# -----------------------------------------------
# Save to matlab file
# -----------------------------------------------
def save_file():
    global emg_tot, quat_tot, acc_tot, gyro_tot, time_tot
    global cdate, pat_name, pat_age, arm
    global condition
    
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
    
    
    if arm.get == 1 :
        dico['arm'] = 'left'
    else :

        dico['arm'] = 'right'
        
    
    sio.savemat('%s_%s.mat' %(cdate, pat_name), dico)
    
    

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
    
    global time_tot
    window = tkinter.Tk()
    window.geometry("500x100") 
    window.title("Instructions")
    
    message = tkinter.StringVar()
    
    def update():
        global condition
        if condition[-1] == 0:
            message.set("Rest")
            #photo = Image.open("rest.jpg")
        elif condition[-1] == 1:
            message.set("Open")    
        elif condition[-1] == 2:
            message.set("Close")
        elif condition[-1] == 3:
            message.set("Open with exo")
        elif condition[-1] == 4:
            message.set("Close with exo")
            
        
        window.after(300, update)
    
    #imglbl = tkinter.Label(image=photo).grid()
    msglbl = tkinter.Label(window, textvariable=message).grid()
    def quitprog ():
        global terminate_program
        terminate_program = True
        window.quit()    
    
    
    # buttons exit and save
    btn_exit = tkinter.Button(window, text="Exit", command=sys.exit, fg='red')
    btn_exit.grid(row=2, column=0, sticky='sw')    

    btn_save = tkinter.Button(window, text="Save", command=quitprog)
    btn_save.grid(row=2, column=2, sticky='se')
    
    window.after(300, update)
    window.mainloop()


# -----------------------------------------------
# main
# -----------------------------------------------
def main(argv):
    import subprocess

    # --- say hello!
    #print('Alive and breathing!\n')
    global file_handle
    global plot_graph, thread_ended
   

    try:
        opts, args = getopt.getopt(argv,"hsgxf:v",["filename="])
    except getopt.GetoptError:
        usage()
    
    GUIwindow_data()
    setup_myo()
    #plot_graphs()
    GUIwindow_instr()
    while not thread_ended:
        pass
    '''txt = ""
    while txt == "":
        txt = input("")'''
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
