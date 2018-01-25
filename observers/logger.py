import logging
from .observer import Observer

class Logger(Observer):
	def opportunity(self, item):
		logging.info('\033[32m%s Amount %f Expected Profit %f\033[0m' % (item[0][1]['case'], item[0][1]['amount'], item[0][1]['profit']) )
