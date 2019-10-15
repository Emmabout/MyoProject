# Overview
This project provides a Python3 software interface to communicate with the Thalmic Myo armband.
The project is built upon the 'myo_raw' library, downloaded from: https://github.com/dzhu/myo-raw
---------
The following library was downloaded instead : https://github.com/dzhu/myo-raw/pull/23/files
It allows to get the raw data from the myo, see the battery life, and more.

# Preliminary steps
Perform these steps:
```
sudo apt-get install python3-pip
sudo -H pip3 uninstall distribute
sudo pip3 install setuptools
sudo pip3 install setuptools --upgrade
```

# Launch installation script
```
./setup.sh
```

# Use the Myo with python
```
python3 myo_test.py
```

# Be able to display images in the GUI
sudo apt-get install python3-pil.imagetk # still not sure

# Author and latest update
Emma Bouton-Bessac 2019.10
