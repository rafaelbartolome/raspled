#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Created by Rafael Bartolome on 2018
#  RaspLed
#  Copyright (c) 2018 RafaelBartolome. All rights reserved.
#

import ConfigParser
import logging.handlers

kMinRefreshInterval = 5
kMaxRefreshInterval = 10*60

class ComunicationConfig:
	def __init__(self, url, refreshInterval):
		self._url = url
		self._refreshInterval = refreshInterval
		if self._refreshInterval < kMinRefreshInterval:
			self._refreshInterval = kMinRefreshInterval
		elif self._refreshInterval > kMaxRefreshInterval:
			self._refreshInterval = kMaxRefreshInterval

	@property
	def url(self):
		return self._url

	@property
	def refreshInterval(self):
	    return self._refreshInterval


class ConfigurationManager:
	def __init__(self):
		self.__execute()

	def __execute(self):
		settings = ConfigParser.ConfigParser()
		settings.read("../raspled.ini")

		self._parseComunications(settings)
		self._debug = settings.getboolean("GENERAL CONFIGURATION", "CONF_DEBUG")
		self._leds = settings.getboolean("GENERAL CONFIGURATION", "CONF_LEDS")
		self._version = settings.get("GENERAL CONFIGURATION", "CONF_VERSION")
		self._logFilename = settings.get("GENERAL CONFIGURATION", "LOG_FILE")
		logLevelString = settings.get("GENERAL CONFIGURATION", "LOG_LEVEL")
		self._logLever = {
			'critical': logging.CRITICAL,
			'error': logging.ERROR,
			'warning': logging.WARNING,
			'info': logging.INFO,
			'debug': logging.DEBUG
		}.get(logLevelString, logging.NOTSET)

	def _parseComunications(self, settings):
		url = settings.get("COMUNICATIONS", "URL")
		refreshInterval = settings.getfloat("COMUNICATIONS", "PLC_REFRESH_INTERVAL")
		self._comunicationConfig = ComunicationConfig(url, refreshInterval)

	@property
	def comunication(self):
		return self._comunicationConfig

	@property
	def showLeds(self):
		return  self._leds

	@property
	def debug(self):
		return self._debug

	@property
	def logFilename(self):
		return self._logFilename

	@property
	def logLevel(self):
		return self._logLever

	@property
	def version(self):
	    return self._version