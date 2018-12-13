#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Created by Rafael Bartolome on 2018
#  RaspLed
#  Copyright (c) 2018 RafaelBartolome. All rights reserved.
#

SiteStateUnknown = 0
SiteStateNotRecheable = 1
SiteStateDown = 2
SiteStateUp = 3

class SiteState:
	"""Booth State"""

	def __init__(self, logger = None):

		if logger != None:
			logger.debug("Parsing PLC Registers")

		self._state = SiteState._defaultSiteState()

		
	@staticmethod
	def _defaultSiteState():
		"""Generate default sireState"""
		return SiteStateUnknown

	@staticmethod
	def defaultSiteState():
		"""Generate default sireState"""
		return SiteState()

	## PUBLIC

	@property
	def state(self):
		"""Current site state"""
		return self._state

	def updateState(self, newState):
		"""Generate default sireState"""
		self._state = newState