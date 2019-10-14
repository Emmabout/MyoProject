# Overview
This project provides a Python3 software interface to communicate with the Thalmic Myo armband.
The project is built upon the 'myo_raw' library, downloaded from: https://github.com/dzhu/myo-raw

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


# Author and latest update
Luca Randazzo, 2018.09