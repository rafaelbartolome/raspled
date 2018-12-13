#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Created by Rafael Bartolome on 2018
#  RaspLed
#  Copyright (c) 2018 RafaelBartolome. All rights reserved.
#

import logging.handlers
from siteState import *
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
			# TODO check site state
			# modBusResponse = self._client.read_holding_registers(kInitialAddress, kRecordsToRead)
			# if not isinstance(modBusResponse.registers, list):
			# 	self._logger.error('### ModBusClient readPLCRegisters exception: check PLC addresses')
			# elif len(modBusResponse.registers) < kRecordsToRead:
			# 	self._logger.error('### ModBusClient readPLCRegisters short response: invalid number of records')

			# siteState = BoothState(modBusResponse.registers, self._logger)
			# if isinstance(boothState, BoothState):
			# 	self._logBoothState(boothState)
			# 	self._boothState = boothState

			return SiteState.defaultSiteState()

		except Exception as e:
			self._logger.error('### WebClient updeteSiteState exception: ' + str(e), exc_info=True)
			raise

