import socket
import hashlib
import threading

DEFAULT_RANGE = 500000
current_start = 0
range_lock = threading.Lock()
result_hash = ""
connected_clients = []
clients_lock = threading.Lock()
found_flag = threading.Event()


"""
Prompts the user to enter a number, pads it with leading zeros to form a 10-digit string,
and computes its MD5 hash hex digest to set as the target for the distributed search.
"""
def get_target_hash():
    target_number = input("Enter the wanted number: ")
    if target_number.isdigit():
        target_number = f"{int(target_number):010d}"
    hash_object = hashlib.md5(target_number.encode())
    return hash_object.hexdigest()

"""
Receives and decodes up to 1024 bytes of UTF-8 data from a connected client socket,
returning the string payload or None if the client disconnects or encounters a socket error.
"""
def handle_client_request(conn, addr):
    try:
        client_data = conn.recv(1024).decode('utf-8')
        if not client_data:
            return None
        print(f"Received data from {addr}")
        return client_data
    except socket.error:
        return None


"""
Iterates through all active client connections stored in the connected clients list
and transmits a STOP message to notify them that the search operation is complete.
"""
def broadcast_stop():
    with clients_lock:
        for client_conn in connected_clients:
            try:
                client_conn.sendall("STOP".encode('utf-8'))
            except socket.error:
                pass


"""
Manages the lifecycle of a connected client by processing work requests,
allocating custom search ranges based on the client CPU capacity, and listening for the solved payload.
"""
def manage_client_session(conn, addr):
    global current_start, result_hash
    with clients_lock:
        connected_clients.append(conn)

    try:
        while not found_flag.is_set():
            client_response = handle_client_request(conn, addr)

            if not client_response:
                break

            if client_response.startswith("GET_WORK"):
                try:
                    _,cpu_count_str = client_response.split(":")
                    client_cpus = int(cpu_count_str)
                except (ValueError, IndexError):
                    client_cpus = 1

                with range_lock:
                    start_range = current_start
                    end_range = start_range + (DEFAULT_RANGE * client_cpus)
                    current_start = end_range

                range_message = f"RANGE:{start_range}:{end_range}:{result_hash}"
                conn.sendall(range_message.encode('utf-8'))
                print(f"Sent range to client {addr}")

            elif client_response.startswith("FOUND"):
                print(f"SUCCESS! Client {addr} found the solution: {client_response}\n")

                found_flag.set()
                broadcast_stop()
                break

            else:
                print(f"Unknown message format from {addr}: {client_response}")
                break

    except socket.error as e:
        print(f"Socket error with client {addr}: {e}")
    finally:
        with clients_lock:
            if conn in connected_clients:
                connected_clients.remove(conn)
        conn.close()
        print(f"Connection closed for: {addr}")

"""
Initializes the TCP server socket, binds to localhost on port 65432,
and continuously listens for incoming client connections, spinning up a dedicated worker thread for each client until a matching hash is found.
"""
def start_server():
    global result_hash
    result_hash = get_target_hash()
    print(f"Target hash to find: {result_hash}")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 65432))
    server.listen()
    print("Server is listening")

    while not found_flag.is_set():
        try:
            server.settimeout(1.0)
            conn, addr = server.accept()

            client_thread = threading.Thread(target=manage_client_session, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()
        except socket.timeout:
            continue

    print("Main server shutting down. Work complete.")
    server.close()


if __name__ == "__main__":
    start_server()
