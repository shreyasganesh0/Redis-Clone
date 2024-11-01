import regex as re
from pydantic import BaseModel
from abc import ABC, abstractmethod
import argparse

class RdbHandler(BaseModel):

    dir: str = "tmp/redis-files"
    file: str = "dump.rdb"

    def setrbd(self, parse_obj: argparse) -> None:
        
        args= parse_obj.parse_args()

        self.dir = args.dir
        self.file = args.dbfilename

        pass
    
    def filehandler(self) -> None:
        
        fpath = f'{self.dir}{self.file}'

        try:
            with open(fpath, 'r') as f:
                f
        
        except FileNotFoundError:
            print ("File is empty")

        return 

    def stringparser(self, s: str) -> str:
        pass

    def intparser(self, s: str) -> str:
        pass

    def parsekeys(self, regex: str) -> str:
        pass





