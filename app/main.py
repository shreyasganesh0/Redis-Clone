import socket  # noqa: F401
import threading
import concurrent.futures

def parse_input(data):
    print("data received is ",data.split("\r\n")[2:])
    return (len(data.split("\r\n",)[2:]) - 1)# count the number of 'PING's sent by the client
    
def socket_accept(server_socket):
    return server_socket.accept()

def client_req_resp(client_socket):
    while True:
            
        data_input = client_socket.recv(2048) # read the data from the client

        if not data_input:
            break

        client_socket.send(b"+PONG\r\n") # reply to the client with pong (hardcoded for now)


    client_socket.close()


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")


    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    
    server_socket.listen(6379) # listen on the port

    # We can use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Start the load operations and mark each future with its URL
        client_set=set()
        while True:
            num_threads = threading.active_count()
            print("Number of active threads:", num_threads)
            client_socket,_=socket_accept(server_socket)
            if client_socket not in client_set:
                client_set.add(client_socket)
                executor.submit(client_req_resp,client_socket)


if __name__ == "__main__":
    main()
