#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Created by Rafael Bartolome on 2018
#  RaspLed
#  Copyright (c) 2018 RafaelBartolome. All rights reserved.
#

import threading
import sys
import logging.handlers
from time import sleep
from configurationManager import ConfigurationManager
from ledsManager import LedsManager
from screenManager import ScreenManager
from webClient import WebClient
from siteState import SiteState

kRaspCheckInterval = 90

class RaspLedApplication():

	def run(self):
		self._setUpSettings()
		self._setUpLogger()

		self._ledsManager = LedsManager(self._settings, self._logger)
		self._ledsManager.resetLeds()
		self._ledsManager.startLeds()
		
		self._setUpScreen()

		self._configureRunLoop()
		
		self._startScreen()
		
	
	def _startScreen(self):
		try:
			self._screenmanager.startScreen()
		except Exception as e:
			self._runLoop = False
			print("RaspLed system error:")
			print("		Could not start user interface  " + str(e))
			print("		Contact system support.")
			self._logger.error("### Error: cant start screen.")
			sys.exit()
	
	def _configureRunLoop(self):
		self._runLoop = True
		try:
			loopThreath = threading.Thread(target=self._mainLoop)
			loopThreath.setDaemon(True)
			loopThreath.start()
		except Exception as e:
			self._runLoop = False
			print("RaspLed system error:")
			print("		Could not create refresh loop  " + str(e))
			print("		Contact system support.")
			self._logger.error("### Error: cant create refresh lood.")
			sys.exit()
	
	def _setUpScreen(self):
		self._screenmanager = ScreenManager(self._settings, self._logger)
		try:
			self._screenmanager.screenCreate()
		except Exception as e:
			print("RaspLed system error:")
			print("		Could not create user interface  " + str(e))
			print("		Contact system support.")
			self._logger.error("### Error: cant create screen.")
			sys.exit()
	
	def _setUpSettings(self):
		try:
			self._settings = ConfigurationManager()
		except Exception as e:
			print("RaspLed system error:")
			print("		Could not load configuration file RaspLed.ini   " + str(e))
			print("		Contact system support.")
			sys.exit()
	
	def _setUpLogger(self):
		# logging
		self._logger = logging.getLogger()
		handler = logging.handlers.RotatingFileHandler(self._settings.logFilename, mode='a', maxBytes=7340032,
													   backupCount=3,
													   encoding=None, delay=False)
		formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
		handler.setFormatter(formatter)
		self._logger.addHandler(handler)
		self._logger.setLevel(self._settings.logLevel)
		self._logger.info('************************************************************************')
		self._logger.info('*****************    RaspLed, starting script    *********************')
		self._logger.info('************************************************************************')

	def _setupWebClient(self):
		self._webClient = WebClient(self._settings.comunication, self._logger)

	def _mainLoop(self):
		self._logger.info('### Main loop')

		self._setupWebClient()
		
		while self._runLoop:
			try:
				siteState = self._webClient.updateSiteState()
				if isinstance(siteState, SiteState):
					self._screenmanager.updateScreen(siteState)
					self._ledsManager.updateLeds(siteState)
						
					sleep(self._settings.comunication.refreshInterval)
				else:
					self._logger.error('### Error: _mainLoop invalid booth state')
					sleep(self._settings.comunication.refreshInterval)

			except Exception as e:
				self._logger.error("### Error: exception in mail loop." + str(e), exc_info=True)
				self._logger.error("### Retrying in " + str(self._settings.comunication.refreshInterval) + " seconds.")
				sleep(self._settings.comunication.refreshInterval)



# *******************************
# **********  main  *************
# *******************************

if __name__ == "__main__":
    app = RaspLedApplication()
    app.run()
