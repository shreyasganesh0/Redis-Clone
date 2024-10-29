import socket  # noqa: F401
import threading
import concurrent.futures
import asyncio
from asyncio import events
from .commandhandler import CommandExecutor


TIMEOUT=5000

class RedisDB:

    
    kvstore: dict = {}


    def parse_input(self, data: bytearray) -> str:
        print("data received is ",data)
        
        data_list = []
        
        data_list = data.decode().split("\r\n") 

        bulk_string_count = data_list[0][1]

        bulk_string_data = [data_list[i] for i in range(1,len(data_list)) if i%2==0] #parses the data and stores only the bulk strings

        print(bulk_string_data)

        command = bulk_string_data[0] # assumes only the first bulk string value will be the command

        method = getattr(CommandExecutor, command.lower())

        resp=method(self, bulk_string_data)

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

        server = await asyncio.start_server(self.client_req_resp,"localhost", 6379)
        
        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    dbobj = RedisDB()
    asyncio.run(dbobj.main())
