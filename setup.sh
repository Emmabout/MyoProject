#!/bin/bash

# Date: 	2018.07.22
# Author: 	Luca Randazzo


#-------------------------
# Variables
#-------------------------
GREEN='\033[0;32m'
PURPLE='\033[0;35m'
NC='\033[0m'
COLOR=${GREEN}

#-------------------------
# numpy
#-------------------------
echo -e "${PURPLE}***********************************************${NC}"
echo -e "${PURPLE}|                [INSTALL.SH]                 |${NC}"
echo -e "${PURPLE}***********************************************${NC}"


#-------------------------
# numpy
#-------------------------
echo -e "${COLOR}[INSTALL.SH] Installing numpy ...${NC}"
pip3 install numpy
# Check
python3 -c "\
try:
    import numpy  
    print('numpy has been correctly installed')
except ImportError:
    print('ERROR: numpy has not been installed')"


#-------------------------
# pyserial
#-------------------------
echo -e "${COLOR}[INSTALL.SH] Installing pyserial ...${NC}"
pip3 install pyserial
# Check
python3 -c "\
try:
    import serial  
    print('pyserial has been correctly installed')
except ImportError:
    print('ERROR: pyserial has not been installed')"


#-------------------------
# pyqtgraph, CHECK IF THIS CAN BE AVOIDED!
#-------------------------
echo -e "${COLOR}[INSTALL.SH] Installing pyqtgraph ...${NC}"
pip3 install pyqtgraph
# Check
python3 -c "\
try:
    import pyqtgraph  
    print('pyqtgraph has been correctly installed')
except ImportError:
    print('ERROR: pyqtgraph has not been installed')"


#-------------------------
# PyQt4, CHECK IF THIS CAN BE AVOIDED!
#-------------------------
echo -e "${COLOR}[INSTALL.SH] Installing PyQt4 ...${NC}"
apt-cache search pyqt
sudo apt-get install python3-pyqt4
# Check
python3 -c "\
try:
    import PyQt4  
    print('PyQt4 has been correctly installed')
except ImportError:
    print('ERROR: PyQt4 has not been installed')"