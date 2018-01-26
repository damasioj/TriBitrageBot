import logging
from .observer import Observer


class Logger(Observer):
    def opportunity(self, item, loggers):
        loggers[0].info('----------------------DEMO-MODE-----------------------')
        loggers[0].info('Profitable trade:')
        loggers[0].info('%s' % (item[0][1]['case']))
        loggers[0].info('Amount %.4f %s Expected Profit %f %s' % (
            item[0][1]['amount'], config.currency_pref, item[0][1]['profit'], config.currency_pref))

        loggers[1].info('----------------------DEMO-MODE-----------------------')
        loggers[1].info('Profitable trade:')
        loggers[1].info('%s' % (item[0][1]['case']))
        loggers[1].info('Amount %.4f %s Expected Profit %f %s' % (
            item[0][1]['amount'], config.currency_pref, item[0][1]['profit'], config.currency_pref))
