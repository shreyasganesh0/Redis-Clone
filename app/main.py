import socket  # noqa: F401
import secrets
import string

import threading
import concurrent.futures
import asyncio
from asyncio import events
from .commandhandler import CommandExecutor
import argparse
from .rbdhandler import RdbHandler


TIMEOUT=5000

class RedisDB:

    host: str = "localhost"    
    kvstore: dict = {}
    two_command: set = set({"CONFIG"})
    dir: str = "app/tmp/redis-files"
    file: str = "dump.rdb"
    port: int = 6379
    replicaof: str ="ismaster"
    master_replid: str
    master_offset: int
    replicas_list: list =[]
    replica_capabilities_list: dict ={}
    propogate_to_replica: set = set(['set','del'])
    replica_connection_obj_pool = {}

    def init_master(self, length=40):
        alphabet = string.ascii_letters + string.digits
        self.master_replid =''.join(secrets.choice(alphabet) for _ in range(length))
        self.master_offset = 0
        pass
    
    def arg_parser_init(self) -> None:

        parser= argparse.ArgumentParser(description = "Parse command line args for testing")

        parser.add_argument('--dir', type = str , default = self.dir, help = "Get the RDB file location")
        
        parser.add_argument('--dbfilename', type = str , default = self.file, help = "Get the RDB file name")

        parser.add_argument('--port', type = int, default = self.port, help = "Get the server port number")

        parser.add_argument('--replicaof', type = str, default = self.replicaof, help = "If flag is mentioned specifies <Master-host> <Master-port>")

        args= parser.parse_args()

        self.dir = args.dir

        self.file = args.dbfilename

        self.port = args.port
        
        self.replicaof = args.replicaof
        pass 

    def rdb_load(self):
        if self.file == 'dump.rdb':
            pass
        rdb_handler_obj = RdbHandler()

        rdb_handler_obj.filehandler(self)
        pass
        
    def parse_input(self, data: bytearray) -> str:
        print("data received is ",data)
        
        data_list = []
        
        data_list = data.decode().split("\r\n") 

        bulk_string_data = [data_list[i] for i in range(1,len(data_list)) if i%2==0] #parses the data and stores only the bulk strings

        print(bulk_string_data)

        command = bulk_string_data[0]


        if command in self.two_command:
            command+=bulk_string_data[1]
        
        print(command)

        command_method = getattr(CommandExecutor, command.lower())

        self.rdb_load()

        resp = command_method(self, bulk_string_data)

        return resp # send decoded string response
    
    async def replica_handshake(self):

        print("here")
        try:
            master_host, master_port = self.replicaof.split(" ")                  
            resp = f"*1\r\n$4\r\nPING\r\n"
            reader, writer = await asyncio.open_connection(master_host,master_port)
            
            resp = resp.encode()
            writer.write(resp)

            response = await reader.read(100)
            print(f"Received response: {response.decode().strip()}")

            replconf1 = f"*3\r\n$8\r\nREPLCONF\r\n$14\r\nlistening-port\r\n${len(str(self.port))}\r\n{self.port}\r\n"
            replconf2 = f"*3\r\n$8\r\nREPLCONF\r\n$4\r\ncapa\r\n$6\r\npsync2\r\n"

            writer.write(replconf1.encode()) 
            response = await reader.read(100)
            print(f"Received response: {response.decode().strip()}")

            writer.write(replconf2.encode()) 
            response = await reader.read(100)
            print(f"Received response: {response.decode().strip()}")

            master_replid = "?"
            master_offset = "-1"
            psync = f"*3\r\n$5\r\nPSYNC\r\n${len(master_replid)}\r\n{master_replid}\r\n${len(master_offset)}\r\n{master_offset}\r\n"

            writer.write(psync.encode()) 
            response = await reader.read(56)
            print(f"Received response: {response}")
            
            return reader, writer

            
        except Exception as e:
            print(f"Error during handshake: {e}")

    def multi_command_parser(self, data_list):
        i=0
        num_elements =0
        while i < len(data_list): 
            if num_elements<1:

                if data_list[i].startswith("*"):
                    num_elements = int(data_list[i].strip("*"))
                    i+=1
                    continue
            else:
                yield data_list[i:i+2*num_elements]
                i+=num_elements*2
    
    def command_sender(self, data):
        print("data is ", data[0:5])
        if data[0:5] == b'REDIS':
            rdb = RdbHandler()
            #rdb.replica_filehandler(self,message)
            resp = -1
            return resp
        if data[0:8] == b'REPLCONF':
            resp = getattr(CommandExecutor, data)
        data = data.decode()
        bulk_string_data = [data[j] for j in range(len(data)) if j%2!=0] #parses the data and stores only the bulk strings

        print(bulk_string_data)

        command = bulk_string_data[0]

        if command in self.two_command:
            command+=bulk_string_data[1]
        
        command = command.lower()

        command_method = getattr(CommandExecutor, command)

        resp = command_method(self, bulk_string_data) 

        return resp

    async def master_listener(self, reader, writer):
        while True:
            print("In master listener", self.port)
            try:
                message = await asyncio.wait_for(reader.read(1000), timeout=30)
                print(message)
                if not message:
                    print("Master connection closed.")
                    break 
                resp=''
                
                data_list = []
                data_list1 = []
                messageparse =""
                d = b"*"

                data_list1 =  [d+e for i,e in enumerate(message.split(d)) if e and i!=0]
                print(data_list1)
                for m in data_list1:
                    if m[1] == b"$":
                        m.strip(b"*")
                    messagparse+= m
                data_list = messageparse.split(b"\r\n")
                print(data_list)

                i=0
                num_elements =0
                
                while i < len(data_list):
                    match(data_list[i][0]):

                        case b"*":
                            num_elements = int(data_list[i].strip(b"*"))
                            i+=1
                            continue

                        case _:
                            if num_elements == 0 :
                                mini_list = data_list[i+1]
                                i+=2
                            else:
                                mini_list = data_list[i:i+2*num_elements]
                                i+=2*num_elements+1

                    print ("mini_list",mini_list)

                    resp = self.command_sender(mini_list)
                    
                
                # Handle the message from the master
            except Exception as e:
                print(f"Error in master listener: {e}")


    async def client_req_resp(self, reader, writer) -> None:

        while True:
            print("here in client", self.port)
            
            try:

                data = await asyncio.wait_for(reader.read(1000), timeout=30)
                if not data:
                    break
                
                resp=''
                
                data_list = []
                
                data_list = data.decode().split("\r\n") 

                resp = self.command_sender(data_list[1:])
                bulk_string_data = [data_list[i] for i in range(1,len(data_list)) if i%2==0] #parses the data and stores only the bulk strings

                print(bulk_string_data)

                command = bulk_string_data[0]

                if command in self.two_command:
                    command+=bulk_string_data[1]
                
                command = command.lower()
                if command == "replconf":

                    self.replica_connection_obj_pool[bulk_string_data[2]] = writer

                command_method = getattr(CommandExecutor, command)

                self.rdb_load()
                
                resp = command_method(self, bulk_string_data)

                resp = resp.encode()

                writer.write(resp)
                print("finished writitng to client", command)
                if command == "psync":
                    with open(f'{self.dir}/{self.file}', 'r') as f: 
                        resp  = bytes.fromhex(f.read())
                        print("here in resync")
                        resp1 = f"${len(resp)}\r\n"
                        writer.write(resp1.encode())
                        writer.write(resp)
                        print(writer.get_extra_info('peername'))

                if command in self.propogate_to_replica:
                    print("Propogating to replicas", resp)
                    for i in self.replicas_list:
                        temp_writer = self.replica_connection_obj_pool[i]
                        temp_writer.write(data)
                        print(f"senf {data} to {self.replica_connection_obj_pool[i]}")


            except asyncio.TimeoutError:
                print("Client request timeout.")
                break
            except Exception as e:
                print(f"Error: {e}")
                break
        writer.close()
        await writer.wait_closed()

    async def main(self):
        print("starting program")
        self.arg_parser_init()
        if self.replicaof == "ismaster":
            self.init_master(40)
        else:
            print("here in client")
            
            reader, writer = await self.replica_handshake()
            
            listener_task = asyncio.create_task(self.master_listener(reader, writer))
            asyncio.gather(listener_task)
        
        print(self.host,self.port)
        
        server = await asyncio.start_server(self.client_req_resp, self.host, self.port) 
        async with server:
            await server.serve_forever()
        

if __name__ == "__main__":
    dbobj = RedisDB()
    asyncio.run(dbobj.main())