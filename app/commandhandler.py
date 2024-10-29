#from abc import ABC, abstractmethod
#from pydantic import BaseModel
from enum import Enum


class Command(Enum):
    ECHO = 1
    PING = 2
    SET = 3
    GET = 4

class CommandExecutor:
    @staticmethod
    def echo( *args):
        obj, message = args[0], args[1][1]
        return ("+"+message+"\r\n")

    @staticmethod
    def ping( *args):
        return "+PONG\r\n"

    @staticmethod
    def set( *args):

        print(args)
        
        obj, key, value = args[0], args[1][1], args[1][2]
        
        obj.kvstore[key] = value
        
        return "+OK\r\n"

    @staticmethod
    def get( *args):

        obj, key = args[0], args[1][1]
        
        val = obj.kvstore[key]
        resp = f'${len(val)}\r\n{val}\r\n'

        return resp
    

# operation = Operation.ADD
# method = getattr(Calculator, operation.name.lower())
# result = method(2, 3
    


    
    

