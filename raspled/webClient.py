#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Created by Rafael Bartolome on 2018
#  RaspLed
#  Copyright (c) 2018 RafaelBartolome. All rights reserved.
#

import logging.handlers
from siteState import *
import httplib
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

			conn = httplib.HTTPConnection("www.google.com")
			conn.request("HEAD", "/")
			googleResponse = conn.getresponse()

			if googleResponse.status == 200:
				#There is 
				self._logger.info('### Google isReachable')
				site = self._comunicationConfig.url
				conn = httplib.HTTPConnection(self._comunicationConfig.url)
				conn.request("HEAD", "/")
				siteResponse = conn.getresponse()
				if siteResponse.status == 200 or siteResponse.status == 301:
					self._logger.info('### Site is up: ' + site)
					siteState.updateState(SiteStateUp)
				else:
					self._logger.info('### Site is down: ' + site + " code: " + str(siteResponse.status) + siteResponse.reason)
					siteState.updateState(SiteStateDown)
			else:
				siteState.updateState(SiteStateNotRecheable)

			return siteState

		except Exception as e:
			self._logger.error('### WebClient updeteSiteState exception: ' + str(e), exc_info=True)
			raise

