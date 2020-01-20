# Overview
This project provides a Python3 software interface to communicate with the Thalmic Myo armband.
The project is built upon the 'myo_raw' library, pull request 23 : https://github.com/dzhu/myo-raw/pull/23/files
It allows to get the raw data from the myo, see the battery life, and more.


---------
The official myo-raw library is : https://github.com/dzhu/myo-raw

# Preliminary steps
Perform these steps:
```
python -m pip install --user numpy scipy matplotlib ipython jupyter pandas sympy nose
sudo apt-get install python3-pip
sudo -H pip3 uninstall distribute
sudo pip3 install setuptools
sudo pip3 install setuptools --upgrade
sudo apt install libcanberra-gtk-module 
```

# Launch installation script
```
./setup.sh
```

# Use the Myo with python
```
python3 ./test2.py
```

# Be able to display images in the GUI
sudo apt-get install python3-pil.imagetk

# Author and latest update
Emma Bouton-Bessac 2020.01
