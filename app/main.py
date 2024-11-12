import socket  # noqa: F401
import threading
import concurrent.futures
import asyncio
from asyncio import events
from .commandhandler import CommandExecutor
import argparse
from .rbdhandler import RdbHandler


TIMEOUT=5000

class RedisDB:

    
    kvstore: dict = {}
    two_command: set = set({"CONFIG"})
    dir: str = "tmp/redis-files"
    file: str = "dump.rdb"
    port: int = 6379
    replicaof: str ="ismaster"

    def arg_parser_init(self) -> None:

        parser= argparse.ArgumentParser(description = "Parse command line args for testing")

        parser.add_argument('--dir', type = str , default = self.dir, help = "Get the RDB file location")
        
        parser.add_argument('--dbfilename', type = str , default = self.file, help = "Get the RDB file name")

        parser.add_argument('--port', type = int, default = self.port, help = "Get the server port number")

        parser.add_argument('--replicaof', type = str, default = self.replicaof, help = "If flag is mentioned specifies <Master-host><Master-port>")

        args= parser.parse_args()

        self.dir = args.dir

        self.file = args.dbfilename

        self.port = args.port
        
        self.replicaof = args.replicaof

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

    async def client_req_resp(self, reader, writer) -> None:
        while True:

            data_input = await asyncio.wait_for(reader.read(2048), timeout=TIMEOUT) # read the data from the client

            if not data_input:
                break
            
            resp=''
            resp = self.parse_input(data_input)
            
            resp = resp.encode()

            writer.write(resp) # reply to the client with pong (hardcoded for now)
        writer.close



    async def main(self):
        # You can use print statements as follows for debugging, they'll be visible when running tests.
        print("Logs from your program will appear here!")
        
        self.arg_parser_init()

        server = await asyncio.start_server(self.client_req_resp,"localhost", self.port)
        
        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    dbobj = RedisDB()
    asyncio.run(dbobj.main())
