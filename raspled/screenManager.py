#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Created by Rafael Bartolome on 2018
#  RaspLed
#  Copyright (c) 2018 RafaelBartolome. All rights reserved.
#

import glib
import gtk
import pango
import copy
import sys
from time import sleep
from threading import Lock
import threading
from siteState import *
from configurationManager import *

kHomePath = "../raspled/"
kTimeIntervalBetweenScreenUpdates = 0.5 # seconds

class ScreenManager:
	"""Manager for screen control. Uses GTK and pango for font rendering """

	def __init__(self, settings, logger):
		self._settings = settings
		self._logger = logger

		self._coldSecuence = 0 # Cold sequence for animation
		self._coldShowing = False
		self._hotShowing = False
		self._standByPatch = 0 # ???
		self._siteState = SiteState.defaultSiteState()
		self._cancelMainLoop = False
		self._lock = Lock()

	# PUBLIC

	def screenCreate(self):
		self._logger.info("*** Screeen Create")

		self._window = self._createWindow()

		self._createImages()
		self._resetImageState()
		self._loadImages()

		self._createFonts()
		self._createLabels()

		self._fixedContainer = self._creteFixedContainer()

		self._window.add(self._fixedContainer)
		self._window.show_all()

		self._hideFullViews()

		gtk.gdk.threads_init()


	def startScreen(self):
		self._logger.info("*** Screeen Started")
		self._updateThread = threading.Thread(target=self._screenLoop)
		self._updateThread.setDaemon(True)
		self._updateThread.start()
		self._mainGTK()


	def updateScreen(self, siteState):
		"""Updates internal data. Can be called form any thread. It actualices value ar main thread"""
		self._logger.debug("*** Screeen Update")
		# assert isinstance(siteState, SiteState)
		try:
			glib.idle_add(self._update_siteState, siteState) # to the main thread
		except Exception as e:
			self._logger.error('*** ScreenManager Error: updateScreen: ' + str(e), exc_info=True)


	# PRIVATE

	def _update_siteState(self, siteState):
		"""Updates private siteState (in main thread)"""
		self._logger.debug("*** Screen _update_siteState")
		self._lock.acquire()
		try:
			self._siteState = siteState
		finally:
			self._lock.release()

	def _screenLoop(self):
		self._logger.info("*** Screen _screenLoop")

		while not self._cancelMainLoop:
			self._lock.acquire()
			try:
				siteState = copy.deepcopy(self._siteState)  # create a copy to avoid race conditions
			except Exception as e:
				self._logger.error('*** ScreenManager Error: _screenLoop lock.acquire' + str(e), exc_info=True)
			finally:
				self._lock.release()
			try:
				# Acquiring the gtk global mutex
				gtk.threads_enter()
				self._logger.debug("*** Screen _screenLoop: Start")
				self._updateLedColor(siteState)
				gtk.threads_leave()
				sleep(kTimeIntervalBetweenScreenUpdates)
			except Exception as e:
				self._logger.error('*** ScreenManager Error: _screenLoop ' + str(e), exc_info=True)
				sleep(kTimeIntervalBetweenScreenUpdates)
				#TODO test if it's needed to cancelMainLoop

	def _mainGTK(self):
		self._logger.debug('*** ScreenManager Main GTK')

		try:
			gtk.main()
		except KeyboardInterrupt:
			self._logger.error('*** ScreenManager GTK.main KeyboardInterrupt: ' + str(e), exc_info=True)
			self._destroy(None)
			raise
		except Exception as e:
			self._logger.error('*** ScreenManager Error: GTK.main: ' + str(e), exc_info=True)
			raise


	def _destroy(self, widget, data=None):
		self._logger.info("*** ScreenManager GTK: destroy signal occurred")
		self._cancelMainLool = True
		gtk.main_quit()
		print("RaspLed: GTK: destroy signal occurred")
		sys.exit()


	def _createWindow(self):
		try:
			window = gtk.Window()
			window.connect("destroy", self._destroy)
			window.set_size_request(480, 320)
			window.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(6400, 6400, 6440))
			window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
			# window.move(0, 0)
			# if not self._settings.debug:
			# 	window.fullscreen()

			return window
		except Exception as e:
			self._logger.error('*** ScreenManager Error: _createWindow' + str(e), exc_info=True)
			raise


	def _createImages(self):
		try:
			self._background = gtk.Image()
			self._greenImage = gtk.Image()
			self._redImage = gtk.Image()
			self._yellowImage = gtk.Image()
			self._blueImage = gtk.Image()

		except Exception as e:
			self._logger.error('*** ScreenManager Error: _createImages' + str(e), exc_info=True)
			raise

	def _resetImageState(self):
		self._greenShowing = False
		self._redShowing = False
		self._yellowShowing = False
		self._blueShowing = False

	def _loadImages(self):
		try:
			#common images
			baseImagesPath = kHomePath + "images/"
			self._background.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(baseImagesPath + "background.png"))
			self._greenImage.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(baseImagesPath + "green.png"))
			self._redImage.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(baseImagesPath + "red.png"))
			self._yellowImage.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(baseImagesPath + "yellow.png"))
			self._blueImage.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(baseImagesPath + "blue.png"))

		except Exception as e:
			self._logger.error('*** ScreenManager Error: _loadImages' + str(e), exc_info=True)
			raise

	def _createFonts(self):
		try:
			self._fontSmall = pango.FontDescription("Helvetica 28")
		except Exception as e:
			self._logger.error('*** ScreenManager Error: _createFonts' + str(e), exc_info=True)
			raise


	def _createLabels(self):
		try:
			self._descriptionLabel = gtk.Label("")
			self._descriptionLabel.modify_font(self._fontSmall)

		except Exception as e:
			self._logger.error('*** ScreenManager Error: _createLabels' + str(e), exc_info=True)
			raise


	def _creteFixedContainer(self):
		try:
			fixedContainer = gtk.Fixed()

			fixedContainer.put(self._background, 0, 0)

			fixedContainer.put(self._greenImage, 0, 0)
			fixedContainer.put(self._redImage, 0, 0)
			fixedContainer.put(self._blueImage, 0, 0)
			fixedContainer.put(self._yellowImage, 0, 0)

			fixedContainer.put(self._descriptionLabel, 110, 260)

			return fixedContainer

		except Exception as e:
			self._logger.error('*** ScreenManager Error: _creteFixedContainer' + str(e), exc_info=True)
			raise


	def _hideFullViews(self):
		try:
			self._greenImage.hide_all()
			self._redImage.hide_all()
			self._blueImage.hide_all()
			self._yellowImage.hide_all()
		except Exception as e:
			self._logger.error('*** ScreenManager Error: _hideFullViews' + str(e), exc_info=True)

	def _updateLedColor(self, siteState):
		self._logger.info("*** Screen _updateLedColor: " + str(siteState.state))
		try:
			self._yellowImage.hide_all()
			self._greenImage.hide_all()
			self._redImage.hide_all()
			self._blueImage.hide_all()
			stringToShow = ""
			if siteState.state == SiteStateUnknown:
				self._yellowImage.show_all()
				stringToShow = "Server Unknown"
			elif siteState.state == SiteStateUp:
				self._greenImage.show_all()
				stringToShow = "Up and running"
			elif siteState.state == SiteStateDown:
				self._redImage.show_all()
				stringToShow = "Server looks Down"
			elif siteState.state == SiteStateNotRecheable:
				self._blueImage.show_all()
				stringToShow = "Not recheable"

			self._descriptionLabel.set_markup('<span color="white">' + stringToShow + "</span>")
		except Exception as e:
			self._logger.error('*** ScreenManager Error: _updateLedColor: ' + str(e))
