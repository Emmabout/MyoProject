from __future__ import print_function
from collections import Counter, deque
import _thread #pyhton2
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
#pyqtgraph.examples.run()



# -----------------------------------------------
# global variables
# -----------------------------------------------
BUFFER_SIZE = 1000
Niteration = 0
file_handle = 0
save_to_file = False
myo = 0
myo_initialized = False
emg_data_buffer = np.zeros((BUFFER_SIZE, 8))
emg_data_latest = np.zeros((1, 8))
quat_data_buffer = np.zeros((BUFFER_SIZE, 4))
quat_data_latest = np.zeros((1, 4))
acc_data_buffer = np.zeros((BUFFER_SIZE, 3))
acc_data_latest = np.zeros((1, 3))
gyro_data_buffer = np.zeros((BUFFER_SIZE, 3))
gyro_data_latest = np.zeros((1, 3))
simulated = False
verbose = False
terminate_program = False
plot_graph = False
#app = QtGui.QApplication([])
app = 0

#win = pg.GraphicsWindow(title="Myo data")
#QtGui.QApplication.setGraphicsSystem('raster')
#mw = QtGui.QMainWindow()
#mw.resize(800,800)


# -----------------------------------------------
# myo thread
# -----------------------------------------------
def thread_myo():
	global emg_data_buffer, emg_data_latest, quat_data_latest, quat_data_buffer, acc_data_latest, acc_data_buffer, gyro_data_latest, gyro_data_buffer, simulated
	global Niteration

	# run loop
	print('Myo thread started.')

	while True:
		# check if thread has to be terminated
		global terminate_program
		if terminate_program:
			print('Myo thread terminated')
			_thread.exit_thread()

		# retrieve last data samples
		if simulated:
			# generate random data
			emg_data_latest = np.random.random_integers(0, 2048, size=(1,8))
			quat_data_latest = np.random.random_integers(0, 2048, size=(1,4))
			acc_data_latest = np.random.random_integers(0, 2048, size=(1,3))
			gyro_data_latest = np.random.random_integers(0, 2048, size=(1,3))
		else:
			# poll myo
			myo.run()

		# save
		if save_to_file:
			# time
			#file_handle.write( str(time.time()) )
			file_handle.write( str(time.strftime("%Hh%Mm%Ss") ) )
			file_handle.write( '\t' )

			# emg
			#for e in emg_data_latest:
			#	file_handle.write( str(e) + ' ' )
			for x in range(0, 7):
				file_handle.write(str(emg_data_latest[0,x]) + ' ')
			file_handle.write( '\t' )

			# quat
			for x in range(0, 3):
				file_handle.write(str(quat_data_latest[0,x]) + ' ')
			file_handle.write( '\t' )

			# acc
			for x in range(0, 2):
				file_handle.write(str(acc_data_latest[0,x]) + ' ')
			file_handle.write( '\t' )

			# gyro
			for x in range(0, 2):
				file_handle.write(str(gyro_data_latest[0,x]) + ' ')
			file_handle.write( '\t' )

			#nl
			file_handle.write('\n')

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

		# print data
		if verbose:
			#print('quaternion:', quat_data_latest, 'accelerations:', acc_data_latest, 'gyroscopes:', gyro_data_latest)
			#print('emg:', emg_data_latest)
			#print('quaternion:', quat_data_latest)
			#print('accelerations:', acc_data_latest)
			print('#',Niteration, ', gyroscopes:', gyro_data_latest)


# -----------------------------------------------
# usage
# -----------------------------------------------
def usage():
	print('usage:')
	print('pyhton myotest.py -option [argument]')
	print(' ')
	print('options:')
	print('	-h:	print this help')
	print('	-x:	simulated myo')
	print('	-g:	real-time graph of the data')
	print('	-s:	save to file [the default filename is the current date&time]')
	print('	-f:	specify a string to append to the filename')
	print('	-v:	verbose')
	print(' ')
	print('example:')
	print('python myotest.py -f test: will create an output file named [date&time]_test\n')



# -----------------------------------------------
# cleanup
# -----------------------------------------------
def cleanup(argument):
	global verbose
	if verbose:
		print('Cleaning up ...')

	# terminate myo thread
	global terminate_program
	terminate_program = True

	global plot_graph
	if plot_graph:
		global app
		#app.closeAllWindows()
		##app.exit()
		##app.quit()

	# disconnect myo
	global simulated, myo_initialized
	if not(simulated):
		if (myo_initialized):
			myo.disconnect()
			print('Myo disconnected')

	# close file
	global save_to_file
	if save_to_file:
		file_handle.close()
		save_to_file=0 #avoids that threads that are still running try and write on the file
		print('File closed')

	if verbose:
		print('Cleaned up.\n')


# -----------------------------------------------
# main
# -----------------------------------------------
def main(argv):
	import subprocess

	# --- say hello!
	#print('Alive and breathing!\n')
	global file_handle, save_to_file
	global plot_graph
	global simulated, verbose


	# --- init variables
	filename = str(time.strftime("%Y.%m.%d.%Hh%M"))


	# --- parse command-line arguments
	if verbose:
		print('Parsing input arguments ...')
		#print ('Number of arguments:', len(sys.argv), 'argument(s)')
		#print ('Arguments:', str(sys.argv))

	try:
		opts, args = getopt.getopt(argv,"hsgxf:v",["filename="])
	except getopt.GetoptError:
		usage()

	for opt, arg in opts:
		if opt == '-h':
			usage()
			cleanup(1)
			sys.exit(0)
		elif opt == '-x':
			print('Option chosen: Simulated Myo.')
			simulated = True
		elif opt == '-g':
			print('Option chosen: Plotting graphs.')
			plot_graph = True
		elif opt == '-s':
			print('Option chosen: Saving to file.')
			save_to_file = True
		elif opt in ("-f", "--filename"):
			save_to_file = True
			filename = filename + '_' + arg
			print('Option chosen: Filename set to: ', filename)
		elif opt == '-v':
			print('Option chosen: Running verbose.')
			verbose = True

	if verbose:
		print('Input arguments parsed.\n')


	# --- open file for storing data
	if save_to_file:
		print('Saving data to file: ', filename)
		file_handle = open(filename,'w')


	# --- setup myo
	global myo, myo_initialized
	print('Setting up myo ...')
	if not(simulated):
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

	else:
		print('Myo simulated')

	_thread.start_new_thread(thread_myo, ())
	print('Myo setup.\n')


	# --- setup QT
	if plot_graph:
		# init window
		app = QtGui.QApplication([])

		print('Starting up plots and QT ...')

		win = pg.GraphicsWindow(title="Myo data")
		win.closeEvent = cleanup
		win.resize(1000,1000)
		win.setWindowTitle('Myo data')
		# pg.setConfigOptions(antialias=True) # Enable antialiasing for prettier plots
		pg.setConfigOption('background', 'k')
		#pg.setConfigOption('background', pg.mkColor(255,255,255) )
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

	# no graphs
	else:
		while(1):
			#if verbose:
			#	print('whiling.. :D')
			1 #do nothing (the threads will perform something, e.g. writing the received values on terminal)



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