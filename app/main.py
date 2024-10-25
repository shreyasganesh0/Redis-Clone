import socket  # noqa: F401

def parse_input(data):
    print("data received is ",data.split("\r\n")[2:])
    return (len(data.split("\r\n",)[2:]) - 1)# count the number of 'PING's sent by the client
    


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    
    server_socket.listen(6379) # listen on the port

    while True:
        client_socket,address = server_socket.accept() # wait for client request and accept the connection
        
        data_input = client_socket.recv(2048) # read the data from the client
        
        #input_len = parse_input(data_input.decode('ASCII'))

        #for i in range(input_len):
        client_socket.send(b"+PONG\r\n") # reply to the client with pong (hardcoded for now)
        
        if not data_input:
            continue
        #break # client closed the connection
    
   # client_socket.close()


if __name__ == "__main__":
    main()
