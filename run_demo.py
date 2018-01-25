import logging
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

    def init_logger(self):
        level = logging.DEBUG
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=level)

    def main(self):
        self.init_logger()
        self.exec_command()    


def main():
    cli = Run()
    cli.main()

if __name__ == '__main__':
    main()    

