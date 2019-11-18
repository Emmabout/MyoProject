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


		# init window
	app = QtGui.QApplication([])

	print('Starting up plots and QT ...')

	win = pg.GraphicsWindow(title="Myo data")
	win.closeEvent = cleanup
	win.resize(1000,1000)
	win.setWindowTitle('Myo data')
	pg.setConfigOptions(antialias=True) # Enable antialiasing for prettier plots
	pg.setConfigOption('background', 'k')
	#pg.setConfigOption('background', pg.mkColor(255,255,255) )
	pg.setConfigOption('foreground', 'w')

	ratio = 1.5
	#win.setLineWidth(100)

	p_emg = win.addPlot(title="EMG")
	p_emg.setXRange(0,BUFFER_SIZE)
	p_emg.setYRange(-2048*7*ratio, 2048)
	p_emg.enableAutoRange('xy', False)
	emg1 = p_emg.plot(pen='r', name="emg1")
	emg2 = p_emg.plot(pen='g', name="emg2")
	emg3 = p_emg.plot(pen='b', name="emg3")
	emg4 = p_emg.plot(pen='c', name="emg4")
	emg5 = p_emg.plot(pen='m', name="emg5")
	emg6 = p_emg.plot(pen='y', name="emg6")
	emg7 = p_emg.plot(pen='w', name="emg7")
	emg8 = p_emg.plot(pen='r', name="emg8")

	win.nextRow()

	p_quat = win.addPlot(title="QUATERNIONs")
	p_quat.setXRange(0,BUFFER_SIZE)
	p_quat.setYRange(-3000*4*ratio, 3000)
	p_quat.enableAutoRange('xy', False)
	quat_a = p_quat.plot(pen='r', name="quaternionA")
	quat_b = p_quat.plot(pen='g', name="quaternionB")
	quat_c = p_quat.plot(pen='b', name="quaternionC")
	quat_d = p_quat.plot(pen='w', name="quaternionD")

	win.nextRow()

	p_acc = win.addPlot(title="ACCELEROMETERs")
	p_acc.setXRange(0,BUFFER_SIZE)
	p_acc.setYRange(-3000*3*ratio, 3000)
	p_acc.enableAutoRange('xy', False)
	acceleration_x = p_acc.plot(pen='r', name="accelerationX")
	acceleration_y = p_acc.plot(pen='g', name="accelerationY")
	acceleration_z = p_acc.plot(pen='b', name="accelerationX")

	win.nextRow()

	p_gyro = win.addPlot(title="GYROSCOPEs")
	p_gyro.setXRange(0,BUFFER_SIZE)
	p_gyro.setYRange(-2048*3*ratio, 2048)
	p_gyro.enableAutoRange('xy', False)
	gyro_x = p_gyro.plot(pen='r', name="gyroX")
	gyro_y = p_gyro.plot(pen='g', name="gyroY")
	gyro_z = p_gyro.plot(pen='b', name="gyroZ")

	win.nextRow()

	def update():
		global verbose
		#if verbose:
		#	print('updating graphs...')
		global emg_data_buffer
		emg1.setData( emg_data_buffer[1:BUFFER_SIZE,0] - 0*2048*ratio )
		emg2.setData( emg_data_buffer[1:BUFFER_SIZE,1] - 1*2048*ratio )
		emg3.setData( emg_data_buffer[1:BUFFER_SIZE,2] - 2*2048*ratio )
		emg4.setData( emg_data_buffer[1:BUFFER_SIZE,3] - 3*2048*ratio )
		emg5.setData( emg_data_buffer[1:BUFFER_SIZE,4] - 4*2048*ratio )
		emg6.setData( emg_data_buffer[1:BUFFER_SIZE,5] - 5*2048*ratio )
		emg7.setData( emg_data_buffer[1:BUFFER_SIZE,6] - 6*2048*ratio )
		emg8.setData( emg_data_buffer[1:BUFFER_SIZE,7] - 7*2048*ratio )
		global quat_data_buffer
		quat_a.setData( quat_data_buffer[1:BUFFER_SIZE,0] - 0*3000*ratio )
		quat_b.setData( quat_data_buffer[1:BUFFER_SIZE,1] - 1*3000*ratio )
		quat_c.setData( quat_data_buffer[1:BUFFER_SIZE,2] - 2*3000*ratio )
		quat_d.setData( quat_data_buffer[1:BUFFER_SIZE,2] - 3*3000*ratio )
		global acc_data_buffer
		acceleration_x.setData( acc_data_buffer[1:BUFFER_SIZE,0] - 0*3000*ratio )
		acceleration_y.setData( acc_data_buffer[1:BUFFER_SIZE,1] - 1*3000*ratio )
		acceleration_z.setData( acc_data_buffer[1:BUFFER_SIZE,2] - 2*3000*ratio )
		global gyro_data_buffer
		gyro_x.setData( gyro_data_buffer[1:BUFFER_SIZE,0] - 0*2048*ratio )
		gyro_y.setData( gyro_data_buffer[1:BUFFER_SIZE,1] - 1*2048*ratio )
		gyro_z.setData( gyro_data_buffer[1:BUFFER_SIZE,2] - 2*2048*ratio )


	timer = QtCore.QTimer()
	timer.timeout.connect(update)
	timer.start(10)

	print('Plots set up.\n')

	if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()





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
