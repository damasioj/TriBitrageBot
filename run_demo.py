import logging
import logging.config
import os
import sys
import config
from triangular import Triangular

class Run():
    def __init__(self):    
        pass


    def create_triangular(self):
        self.triangular = Triangular()


    def exec_command(self):
        config.demo_mode = True
        self.create_triangular()
        self.triangular.loop()
    

    #def init_logger(self):
    #    logging.config.fileConfig('logger.config')
    #    logger = logging.getLogger('main_logger')
    
    def main(self):
        #self.init_logger()
        self.exec_command()    


def main():
    cli = Run()
    cli.main()

if __name__ == '__main__':
    main()    

