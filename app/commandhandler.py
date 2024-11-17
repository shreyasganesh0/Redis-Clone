import re
#from abc import ABC, abstractmethod
#from pydantic import BaseModel
from enum import Enum
from datetime import timedelta, timezone, datetime
from .errorhandler.exceptions import ReplConfException




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
        
        obj.kvstore[key] = (value,int(timeout),int(datetime.now(timezone.utc).timestamp()*1000))

        print(obj.kvstore)
        
        return "+OK\r\n"

    @staticmethod
    def get( *args):

        obj, key = args[0], args[1][1]

        
        val, timeout, time_insert = obj.kvstore.get(key, ["",int(datetime.now(timezone.utc).timestamp()*1000)+10000000,0])

        print(int(datetime.now(timezone.utc).timestamp()*1000)-time_insert, timeout, "checking set")
       
        if timeout==-1:
            return f'${len(val)}\r\n{val}\r\n'
       
        if int(datetime.now(timezone.utc).timestamp()*1000)-time_insert >= timeout:
            del obj.kvstore[key]
            val=""

        if val=="":
            print("here val is null")
            resp = "$-1\r\n"
        else:
            resp = f'${len(val)}\r\n{val}\r\n'
        
        return resp
    
    @staticmethod
    def configget( *args) -> str:

        serverobj, req = args[0], args[1][2]

        req_size = len(req)

        if req == "dir":
            path = serverobj.dir
            path_size = len(path)
        
        elif req == "dbfilename":
            path = serverobj.dbfilename
            path_size = len(path)

        resp = f"*2\r\n${req_size}\r\n{req}\r\n${path_size}\r\n{path}\r\n"

        return resp   
    
    @staticmethod
    def keys( *args):
        print(args)

        obj, regex = args[0], args[1][1]
        if regex == "*":
            regex = "."+regex
        print(regex)
        reObj = re.compile(regex)
        resp = []

        for key in obj.kvstore:
                print(key)
                if(reObj.match(key)):
                    resp.append(f'${len(key)}\r\n{key}\r\n')
        print(resp)
        return f"*{len(resp)}\r\n"+"".join(resp)

    @staticmethod
    def info( *args):
        obj, param = args[0], args[1][1]

        if param != None:
            match(param):
                case "replication":
                    role = "master" if obj.replicaof == "ismaster" else "slave"

                    if obj.replicaof == "ismaster": 
                        master_replid = obj.master_replid
                        master_offset = obj.master_offset
                        resp = f"${len(role)+5+len(master_replid)+14+20+2+2}\r\nrole:{role}\r\nmaster_replid:{master_replid}\r\nmaster_repl_offset:{master_offset}\r\n"
                    else:
                        resp = f"${len(role)+5}\r\nrole:{role}\r\n" 
        return resp
    
    @staticmethod
    def replconf( *args):
        print("here in repl")
        obj = args[0]
        resp = ""
        if args[1][1] == "listening-port":
            obj.replicas_list.append(args[1][2])
            resp = "+OK\r\n"
        elif args[1][1] == "capa":
            obj.replica_capabilities_list[obj.replicas_list[-1]] = args[1][2]
            resp = "+OK\r\n"
        else:
            raise ReplConfException()
        return resp