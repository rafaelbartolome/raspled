#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Created by Rafael Bartolome on 2018
#  RaspLed
#  Copyright (c) 2018 RafaelBartolome. All rights reserved.
#

import logging.handlers
import subprocess
from time import sleep

# logging
logger = logging.getLogger()
handler = logging.handlers.RotatingFileHandler('raspled.log', mode='a', maxBytes=7340032, backupCount=3, encoding=None, delay=False)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

while True:
	try:
		logger.info('************************************************************************')
		logger.info('**************        RaspLed, starting script       *******************')
		logger.info('************************************************************************')

		command = 'sudo python /home/pi/raspled/raspled.py'.split()
		p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		while True:
			retcode = p.poll()  # returns None while subprocess is running
			line = p.stdout.readline()
			logger.info('>>>>> ' + line)
			if retcode is not None:
				logger.info('>>>>> ERROR: Child was terminated by signal: ' + str(retcode))
				break

	except OSError as e:
		logger.error('>>>>> Execution failed: ' + str(e), exc_info=True)
		sleep(1)
