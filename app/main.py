import socket  # noqa: F401
import threading
import concurrent.futures
import asyncio
from asyncio import events
from typing import ByteString

TIMEOUT=5000



def parse_input(data: ByteString) -> str:
    print("data received is ",data)
    data_list = []
    data_list = data.decode().split("\r\n") 

    bulk_string_count = data_list[0][1]
    #print("number of bulk strings", bulk_string_count)

    bulk_string_data = [data_list[i] for i in range(1,len(data_list)) if i%2==0] #parses the data and stores only the bulk strings

    #print(bulk_string_data)

    command = bulk_string_data[0] # assumes only the first bulk string value will be the command

    #print(command)

    #below are hard coded implementations for command parsing, will abstract this away in the future
    if command == "ECHO":
        resp = bulk_string_data[1]

    elif command == "PING":
        resp = "PONG"

    
    return resp # send decoded string response
    
def socket_accept(server_socket):
    return server_socket.accept()

async def client_req_resp(reader,writer):
    while True:

        data_input = await asyncio.wait_for(reader.read(2048), timeout=TIMEOUT) # read the data from the client

        if not data_input:
            break
        resp=''
        resp = parse_input(data_input)
        
        resp = "+"+resp+"\r\n" # creates a  RESP simple string from the response will probably need a method to send any form of output depending on command in the future
        resp = resp .encode()
        writer.write(resp) # reply to the client with pong (hardcoded for now)
    writer.close

async def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    server = await asyncio.start_server(client_req_resp,"localhost", 6379)
    
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
