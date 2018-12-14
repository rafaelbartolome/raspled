#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Created by Rafael Bartolome on 2018
#  RaspLed
#  Copyright (c) 2018 RafaelBartolome. All rights reserved.
#

import logging.handlers
import socket
from siteState import *
import httplib
import urllib2
from configurationManager import ComunicationConfig

class WebClient:

	def __init__(self, comunicationConfig, logger):
		self._comunicationConfig = comunicationConfig
		self._logger = logger
		self._siteState = SiteState._defaultSiteState()


	def updateSiteState(self):
		"""Try to read site state and returns a siteState object or throws"""
		self._logger.debug('### Reading Site State')

		try:
			siteState = SiteState.defaultSiteState()
			site = self._comunicationConfig.url

			isConnected = self.isConnected()
			if isConnected:
				#There is connection
				self._logger.info('### Internet isReachable')

				if self.canOpenUrl(site):
					self._logger.info('### Site is up: ' + site)
					siteState.updateState(SiteStateUp)
				else:
					self._logger.info('### Site is down: ' + site)

					siteState.updateState(SiteStateDown)
				
				# site = self._comunicationConfig.url
				# conn = httplib.HTTPConnection(self._comunicationConfig.url, timeout=2)
				# conn.request("HEAD", "/")
				# siteResponse = conn.getresponse()
				# if siteResponse.status == 200 or siteResponse.status == 301:
				# 	self._logger.info('### Site is up: ' + site)
				# 	siteState.updateState(SiteStateUp)
				# else:
				# 	self._logger.info('### Site is down: ' + site + " code: " + str(siteResponse.status) + siteResponse.reason)
				# 	siteState.updateState(SiteStateDown)
			else:
				self._logger.info('### Internet is NOT Reachable')
				siteState.updateState(SiteStateNotRecheable)

			return siteState

		except Exception as e:
			self._logger.error('### WebClient updeteSiteState exception: ' + str(e), exc_info=True)
			raise

	def isConnected(self):
		try:
			socket.setdefaulttimeout(2)
			socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53)) #Google default DNS
			return True
		except Exception as e:
			self._logger.error('### WebClient isConnected check socket exception: ' + str(e), exc_info=True)
			return False

	def canOpenUrl(self, site):
		try:
			urllib2.urlopen(site, timeout=2)
			return True
		except urllib2.URLError as e: 
			self._logger.error('### WebClient canOpenUrl  exception: ' + str(e), exc_info=True)
			return False