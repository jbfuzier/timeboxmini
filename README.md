# timeboxmini
Python mqtt daemon to talk with timebox mini

### 0. Requirements 
Bluetooth installed & configured with a bluetoth dongle.
On debian : `apt-get install bluetooth`

To check that the dongle is working properly : `blescan`

Python requirements (see requirements.txt) : `pip install -r requirements.txt`. A C compiler & bluetooth dev headers are required, on debian : `apt install libbluetooth-dev build-essential`
