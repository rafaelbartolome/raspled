# RaspLed 

RaspLed is a software/hardware demo tool to check if a web site is up or down.
Is order to present the status of the site a RGB led is used.

<p align="center">
  <img src="https://rafaelbartolome.github.io/raspled/md-img/board.png" alt="Board"
       width="502" height="700">
</p>

## List of materials

* Raspberry Pi 3 (should work in other models) + power source + SD card
* Proto board for rapid prototyping
* RGB LEd
* Resistors x3
* Some small wires

Optional:

* Monitor + keyboard + mouse

## How It Works

Small program that runs in the rasp and check if there is internet reachable and later an internet site.

LED status:

* **yellow** - Connection unknow
* **blue** - Internet not recheable
* **red** - Site down
* **green** - Site Up & running

## Board pinout

For this demo GPIO ports 17,27 and 22 are used, but can be modified at `raspled/ledsManager.py`

```python
kRedPinAddress = 17
kGreenPinAddress = 27
kBluePinAddress = 22
```

<p align="center">
  <img src="https://rafaelbartolome.github.io/raspled/md-img/rasp.png" alt="Board"
       width="540" height="180">
</p>

Be aware of GPIO adresses are not pin position. GPIO17 is PIN11

## LED pinout

Check your RBG LED datasheed, but most common configuration is:

<p align="center">
  <img src="https://rafaelbartolome.github.io/raspled/md-img/led.png" alt="Board"
       width="111" height="309">
</p>

* Pin1 - Red channel
* Pin2 - Cathode
* Pin3 - Green channel
* Pin4 - Blue channel

Don't forget to attach a small resistor to color channels.

## Software dependencies

* [python-gtk2](https://pygobject.readthedocs.io/en/latest/) for UI
* Pango for text rendering 
* [pi-blaster](https://github.com/sarfata/pi-blaster) for IO comunications

<p align="center">
  <img src="https://rafaelbartolome.github.io/raspled/md-img/demo.jpg" alt="Demo"
       width="600" height="521">
</p>

## Usage

First, install all software dependencies.

Clone this repo and configure appropiate path on files `raspled.ini`, `startRaspLed.py`, `raspled/configurationManager.py` and `raspled/screenManager.py`

By default `/home/pi` is configured.

Run:

```sh
$ python startRaspLed.py
```

It's recomended to install it when starting GUI, this way it can works automatically, with or without monitor attached:

```sh
$ sudo nano ~/.config/lxsession/LXDE-pi/autostart
```

```
@lxpanel --profile LXDE
@pcmanfm --desktop --profile LXDE
@xscreensaver -no-splash
@xset s noblank
@xset s off
@xset -dpms
@unclutter -idle 0.1 -root
@sudo python /home/pi/startRaspLed.py
```
All traces go to file `raspled.log`, it's recommended to check it of when looking for problems.

```sh
$ tail -f ./raspled.log
````

## Config

Edit `raspled.ini` that contains basic configuration.
Most important options are:
* Log level
* Site URL
* Pooling interval (seconds)

<p align="center">
  <img src="https://rafaelbartolome.github.io/raspled/md-img/final.jpg" alt="Final demo"
       width="600" height="450">
</p>

## Disclaimer

This is a demo project executed in about 6 hours in order to refresh some python concepts and to play a little bit with leds and wires. Don't look for a nice implementation in code ;)

Any doubt or comment is welcomed.
