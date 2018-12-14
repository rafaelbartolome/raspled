#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Created by Rafael Bartolome on 2018
#  RaspLed
#  Copyright (c) 2018 RafaelBartolome. All rights reserved.
#

import os
from siteState import *
from threading import Lock
import threading
import glib
from time import sleep
import copy

# LEDS
kLedsProgramSteps = 100
kTimeIntervalBetweenLedsUpdates = 1 # seconds

# Leds programs [RedInit, RedEnd, GreenInit, GreenEnd, BlueInit, BlueEnd]
ProgramBlue = [0, 0, 0, 0, 0, 255]  
ProgramRed = [0, 255, 0, 0, 0, 0]  
ProgramGreen = [0, 0, 0, 255, 0, 0]  
ProgramYellow = [0, 255, 0, 80, 0, 255]  

# Color PIN addresses (GPIO positions)
kRedPinAddress = 17
kGreenPinAddress = 27
kBluePinAddress = 22

# LEds state
StateUnknown = 0
StateNotRecheable = 1
StateDown = 2
StateUp = 3

# WaitingTime (segs)
StateUnknownTime = 0
StateNotRecheableTime = 3
StateDownTime = 8
StateUpTime = 1

StateUnknownTimeOn = 1
StateNotRecheableTimeOn = 1
StateDownTimeOn = 0.5
StateUpTimeOn = 2

# Led steps (segs)
StateUnknownSteps = 100
StateNotRecheableSteps = 20
StateDownSteps = 10
StateUpSteps = 20

class LedsManager:
	"""Manager for Leds control. Uses Pi-Blaster library in order to send OS cmds to /dev/pi-blaster"""

	def __init__(self, settings, logger):
		self._settings = settings
		self._logger = logger
		self._previousState = StateUnknown
		self._previousProgram = ProgramYellow
		self._currentRedValue = 0
		self._currentGreenValue = 0
		self._currentBlueValue = 0
		self._lock = Lock()
		self._cancelMainLoop = False
		self._siteState = SiteState.defaultSiteState()


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
		
	def updateLeds(self, siteState):
		"""Updates internal data. Can be called form any thread. It actualices value ar main thread"""
		self._logger.debug("%%% LEDS Update")
		assert isinstance(siteState, SiteState)
		try:
			glib.idle_add(self._update_siteState, siteState)  # to the main thread
		except Exception as e:
			self._logger.error('%%% LEDS Error: updateScreen: ' + str(e), exc_info=True)
	
	# PRIVATE
	
	def _update_siteState(self, siteState):
		"""Updates private siteState (in main thread)"""
		self._logger.debug("%%% LEDS Updating leds")
		self._lock.acquire()
		try:
			self._siteState = siteState
		finally:
			self._lock.release()
		
	def _leedsLoop(self):
		self._logger.info("%%% LEDS _leedsLoop")
		
		while not self._cancelMainLoop:
			# self._logger.info("%%% LEDS _leedsLoop again")
			self._lock.acquire()
			try:
				siteState = copy.deepcopy(self._siteState)  # create a copy to avoid race conditions
			except Exception as e:
				self._logger.error('%%% LEDS  Error: _leedsLoop lock.acquire' + str(e), exc_info=True)
			finally:
				self._lock.release()
				
			ledsLog = ""
			newProgram = []
			if siteState.state == SiteStateDown: # Red
				newState = StateDown
				newProgram = ProgramRed
				ledsLog = "Red"
			elif siteState.state == SiteStateNotRecheable:  # Blue
				newState = StateNotRecheable
				newProgram = ProgramBlue
				ledsLog = "Blue"
			elif siteState.state == SiteStateUp:  # Green
				newState = StateUp
				newProgram = ProgramGreen
				ledsLog = "Green"
			elif siteState.state == SiteStateUnknown:  # Yellow
				newState = StateUnknown
				newProgram = ProgramYellow
				ledsLog = "Yellow"
			else:  # Resto
				newState = StateUnknown
				newProgram = ProgramYellow
	
			if self._previousState != newState:
				self._logger.info("%%% LEDS  WriteLeds: state " + str(self._previousState) + " " + ledsLog)
				self._previousState = newState
				self._writeSingle([self._previousProgram[0],
							 newProgram[0],
							 self._previousProgram[2],
							 newProgram[2],
							 self._previousProgram[4],
							 newProgram[4]])
				self._previousProgram = newProgram
			else:
				self._logger.info("%%% LEDS _leedsLoop again state " + str(self._previousState) + " " + ledsLog)
				self._writeProgram(self._previousProgram)

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
		sleepTime = 0
		timeOn = 0
		steps = kLedsProgramSteps
		if self._previousState == StateUnknown:
			sleepTime = StateUnknownTime
			steps = StateUnknownSteps
			timeOn = StateUnknownTimeOn
		elif self._previousState == StateNotRecheable:
			sleepTime = StateNotRecheableTime
			steps = StateNotRecheableSteps
			timeOn = StateNotRecheableTimeOn
		elif self._previousState == StateDown:
			sleepTime = StateDownTime
			steps = StateDownSteps
			timeOn = StateDownTimeOn
		else:
			sleepTime = StateUpTime
			steps = StateUpSteps
			timeOn = StateUpTimeOn

		iniR = ledProgram[0]
		endR = ledProgram[1]
		self._currentRedValue = iniR
		aveR = (endR - iniR) / steps

		iniG = ledProgram[2]
		endG = ledProgram[3]
		self._currentGreenValue = iniG
		aveG = (endG - iniG) / steps

		iniB = ledProgram[4]
		endB = ledProgram[5]
		self._currentBlueValue = iniB
		aveB = (endB - iniB) / steps


		for i in range(0, steps):
			self._currentRedValue += aveR
			self._currentGreenValue += aveG
			self._currentBlueValue += aveB
			self._writeColor(self._currentRedValue, self._currentGreenValue, self._currentBlueValue)

		sleep(timeOn)

		for i in range(0, steps):
			self._currentRedValue -= aveR
			self._currentGreenValue -= aveG
			self._currentBlueValue -= aveB
			self._writeColor(self._currentRedValue, self._currentGreenValue, self._currentBlueValue)

		sleep(sleepTime)

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
