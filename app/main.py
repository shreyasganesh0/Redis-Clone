import socket  # noqa: F401
import threading
import concurrent.futures
import asyncio
from asyncio import events

TIMEOUT=5000

def parse_input(data):
    print("data received is ",data.split("\r\n")[2:])
    return (len(data.split("\r\n",)[2:]) - 1)# count the number of 'PING's sent by the client
    
def socket_accept(server_socket):
    return server_socket.accept()

async def client_req_resp(reader,writer):
    while True:

        data_input = await asyncio.wait_for(reader.read(2048), timeout=TIMEOUT) # read the data from the client

        if not data_input:
            break

        writer.write(b"+PONG\r\n") # reply to the client with pong (hardcoded for now)
    writer.close

async def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    server = await asyncio.start_server(client_req_resp,"localhost", 6379)
    
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
