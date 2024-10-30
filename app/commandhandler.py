#from abc import ABC, abstractmethod
#from pydantic import BaseModel
from enum import Enum
from datetime import timedelta, timezone, datetime



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
        if len(args[1])<=3:
            obj, key, value = args[0], args[1][1], args[1][2]
            timeout = -1
        
        else:
            flag = True
            obj, key, value, timeout = args[0], args[1][1], args[1][2], args[1][4]
        
        obj.kvstore[key] = (value,timeout,datetime.now(timezone.utc))

        print(obj.kvstore)
        
        return "+OK\r\n"

    @staticmethod
    def get( *args):

        obj, key = args[0], args[1][1]

        
        val, timeout, time_insert = obj.kvstore.get(key, ["",10000000,0])

        if timeout==-1:
            return f'${len(val)}\r\n{val}\r\n'
       
        if datetime.now(timezone.utc)-time_insert > timedelta(milliseconds=int(timeout)):
            del obj.kvstore[key]
            val=""

        if val=="":
            print("here")
            resp = "$-1\r\n"
        else:
            resp = f'${len(val)}\r\n{val}\r\n'
        
        return resp
    
    @staticmethod
    def configget( *args) -> str:

        print(args)

        obj, req = args[0], args[1][2]

        req_size = len(req)


        if req == "dir":
            path = obj.dir
            path_size = len(path)
        
        elif req == "dbfilename":
            path = obj.file
            path_size = len(path)

        
        resp = f"*2\r\n${req_size}\r\n{req}\r\n${path_size}\r\n{path}\r\n"

        return resp      

# operation = Operation.ADD
# method = getattr(Calculator, operation.name.lower())
# result = method(2, 3
    
