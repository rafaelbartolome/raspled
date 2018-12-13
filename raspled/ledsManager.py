#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Created by Rafael Bartolome on 2018
#  RaspLed
#  Copyright (c) 2018 RafaelBartolome. All rights reserved.
#

import os
from boothState import *
from threading import Lock
import threading
import glib
from time import sleep
import copy

# LEDS
kLedsProgramSteps = 100
kTimeIntervalBetweenLedsUpdates = 0.3 # seconds

# Leds programs [RedInit, RedEnd, GreenInit, GreenEnd, BlueInit, BlueEnd]
ProgramCold = [0, 0, 0, 0, 255, 90]  # Azul
ProgramHot = [255, 90, 0, 0, 0, 0]  # Rojo
ProgramDry = [0, 0, 255, 90, 0, 0]  # Verde
ProgramMaintenance = [255, 255, 30, 30, 0, 0]  # Naranja rojizo
ProgramStandBy = [255, 100, 255, 100, 255, 100]  # Blanco

# Color PIN addresses (GPIO positions)
kRedPinAddress = 24
kGreenPinAddress = 18
kBluePinAddress = 23

# LEds state
StateHot = 1
StateCold = 2
stateDry = 3
StateMaintenance = 4
StateNone = 0

class LedsManager:
	"""Manager for Leds control. Uses Pi-Blaster library in order to send OS cmds to /dev/pi-blaster"""

	def __init__(self, settings, logger):
		self._settings = settings
		self._logger = logger
		self._previousState = StateNone
		self._previousProgram = ProgramStandBy
		self._currentRedValue = 0
		self._currentGreenValue = 0
		self._currentBlueValue = 0
		self._lock = Lock()
		self._cancelMainLoop = False
		self._boothState = BoothState.defaultBoothState()


	def resetLeds(self):
		"""Reset Leds"""
		self._logger.debug("%%% LEDS Reset leds")

		self._writePWM(kRedPinAddress, 0)
		self._writePWM(kGreenPinAddress, 0)
		self._writePWM(kBluePinAddress, 0)
	
	def startLeds(self):
		self._logger.info("%%% LEDS startLeds ")
		self._updateThread = threading.Thread(target=self._leedsLoop)
		self._updateThread.setDaemon(True)
		self._updateThread.start()
		
	def updateLeds(self, boothState):
		"""Updates internal data. Can be called form any thread. It actualices value ar main thread"""
		self._logger.debug("%%% LEDS Update")
		assert isinstance(boothState, BoothState)
		try:
			glib.idle_add(self._update_boothState, boothState)  # to the main thread
		except Exception as e:
			self._logger.error('%%% LEDS Error: updateScreen: ' + str(e), exc_info=True)
	
	# PRIVATE
	
	def _update_boothState(self, boothState):
		"""Updates private boothState (in main thread)"""
		self._logger.debug("%%% LEDS Updating leds")
		self._lock.acquire()
		try:
			self._boothState = boothState
		finally:
			self._lock.release()
		
	def _leedsLoop(self):
		self._logger.info("%%% LEDS _leedsLoop")
		
		while not self._cancelMainLoop:
			self._lock.acquire()
			try:
				boothState = copy.deepcopy(self._boothState)  # create a copy to avoid race conditions
			except Exception as e:
				self._logger.error('%%% LEDS  Error: _leedsLoop lock.acquire' + str(e), exc_info=True)
			finally:
				self._lock.release()
				
			ledsLog = ""
			newProgram = []
			if boothState.colorLeds == LedColorRed: # Calor
				newState = StateHot
				newProgram = ProgramHot
				ledsLog = "Hot"
			elif boothState.colorLeds == LedColorBlue:  # Frio
				newState = StateCold
				newProgram = ProgramCold
				ledsLog = "Cold"
			elif boothState.colorLeds == LedColorWhite:  # Secado
				newState = stateDry
				newProgram = ProgramDry
				ledsLog = "Drying"
			elif boothState.colorLeds == LedColorOrange:  # Mantenimiento
				newState = StateMaintenance
				newProgram = ProgramMaintenance
				ledsLog = "Maintenance"
			else:  # Resto
				newState = StateNone
				newProgram = ProgramStandBy
	
			if self._previousState != newState:
				self._logger.info("%%% LEDS  WriteLeds: Changing " + ledsLog)
				self._previousState = newState
				self._writeSingle([self._previousProgram[0],
							 newProgram[0],
							 self._previousProgram[2],
							 newProgram[2],
							 self._previousProgram[4],
							 newProgram[4]])
				self._previousProgram = newProgram
			else:
				self._writeProgram(newProgram)
			
			sleep(kTimeIntervalBetweenLedsUpdates)

	def _writePWM(self, pin, value):
		"""Writes single pin with value"""

		cmd = "echo " + str(pin) + "=" + repr(float(value) / 255) + " > /dev/pi-blaster"
		if self._settings.showLeds:
			self._lock.acquire()
			try:
				os.system(cmd)
			except Exception as e:
				self._logger.error('%%% LEDS LedsManager Error: _writeColor lock.acquire' + str(e), exc_info=True)
			finally:
				self._lock.release()


	def _writeProgram(self, ledProgram):
		"""Writes leds program from start value to end value and returns to start value (fadeIn/fadeOut)"""

		iniR = ledProgram[0]
		endR = ledProgram[1]
		self._currentRedValue = iniR
		aveR = (endR - iniR) / kLedsProgramSteps

		iniG = ledProgram[2]
		endG = ledProgram[3]
		self._currentGreenValue = iniG
		aveG = (endG - iniG) / kLedsProgramSteps

		iniB = ledProgram[4]
		endB = ledProgram[5]
		self._currentBlueValue = iniB
		aveB = (endB - iniB) / kLedsProgramSteps

		for i in range(0, kLedsProgramSteps):
			self._currentRedValue += aveR
			self._currentGreenValue += aveG
			self._currentBlueValue += aveB
			self._writeColor(self._currentRedValue, self._currentGreenValue, self._currentBlueValue)

		for i in range(0, kLedsProgramSteps):
			self._currentRedValue -= aveR
			self._currentGreenValue -= aveG
			self._currentBlueValue -= aveB
			self._writeColor(self._currentRedValue, self._currentGreenValue, self._currentBlueValue)


	def _writeSingle(self, ledProgram):
		"""Writes leds program from start value to end value (fadeIn)"""

		iniR = ledProgram[0]
		endR = ledProgram[1]
		self._currentRedValue = iniR
		aveR = (endR - iniR) / kLedsProgramSteps

		iniG = ledProgram[2]
		endG = ledProgram[3]
		self._currentGreenValue = iniG
		aveG = (endG - iniG) / kLedsProgramSteps

		iniB = ledProgram[4]
		endB = ledProgram[5]
		self._currentBlueValue = iniB
		aveB = (endB - iniB) / kLedsProgramSteps

		for i in range(0, kLedsProgramSteps):
			self._currentRedValue += aveR
			self._currentGreenValue += aveG
			self._currentBlueValue += aveB
			self._writeColor(self._currentRedValue, self._currentGreenValue, self._currentBlueValue)


	def _writeColor(self, redValue, greenValue, blueValue):
		"""Writes RGB values to the right pin addreeses"""
		cmd = "echo " + \
			  str(kRedPinAddress) + "=" + repr(float(redValue) / 255) + " > /dev/pi-blaster && echo " + \
			  str(kGreenPinAddress) + "=" + repr(float(greenValue) / 255) + " > /dev/pi-blaster && echo " + \
			  str(kBluePinAddress) + "=" + repr(float(blueValue) / 255) + " > /dev/pi-blaster"
		if self._settings.showLeds:
			self._lock.acquire()
			try:
				os.system(cmd)
			except Exception as e:
				self._logger.error('%%% LEDS LedsManager Error: _writeColor lock.acquire' + str(e), exc_info=True)
			finally:
				self._lock.release()
