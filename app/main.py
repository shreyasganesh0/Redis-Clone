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
    dir: str = "tmp/redis-files"
    file: str = "dump.rdb"
    port: int = 6379
    replicaof: str ="ismaster"
    master_replid: str
    master_offset: int

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

        bulk_string_count = data_list[0][1]

        bulk_string_data = [data_list[i] for i in range(1,len(data_list)) if i%2==0] #parses the data and stores only the bulk strings

        print(bulk_string_data)

        command = bulk_string_data[0]


        if command in self.two_command:
            command+=bulk_string_data[1]
        
        print(command)

        command_method = getattr(CommandExecutor, command.lower())

        self.rdb_load()

        print(self.kvstore,"kv")

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
            response = await reader.read(100)
            print(f"Received response: {response.decode().strip()}")

            # Close the connection
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            print(f"Error during handshake: {e}")


    async def client_req_resp(self, reader, writer) -> None:

        while True:
            print("here in client")
            
            try:
                data_input = await asyncio.wait_for(reader.read(2048), timeout=TIMEOUT) # read the data from the client

                if not data_input:
                    break
                
                resp=''
                resp = self.parse_input(data_input)
                
                resp = resp.encode()

                writer.write(resp) # reply to the client with pong (hardcoded for now)
            except asyncio.TimeoutError:
                print("Client request timeout.")
                break
            except Exception as e:
                print(f"Error: {e}")
                break
        writer.close()
        await writer.wait_closed()

    async def main(self):
        # You can use print statements as follows for debugging, they'll be visible when running tests.
        print("Logs from your program will appear here!")
        
        self.arg_parser_init()
        if self.replicaof == "ismaster":
            self.init_master(40)
        else:
            print("here in client")
            await self.replica_handshake()
        print(self.host,self.port)
        server = await asyncio.start_server(self.client_req_resp,self.host, self.port)
        
        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    dbobj = RedisDB()
    asyncio.run(dbobj.main())