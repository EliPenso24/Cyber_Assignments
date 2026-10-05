import socket
import os
import threading
import hashlib

SERVER_IP = "127.0.0.1"
SERVER_PORT = 65432
stop_event = threading.Event()
found_answer = None


"""
Performs brute force MD5 hash cracking over a specified numeric range by padding numbers to 10 digits,
comparing their hashes against a target hash, and setting the global answer when a match is found.
"""
def md5_worker(start_num, end_num, target_hash):
    global stop_event, found_answer
    for number in range(start_num, end_num + 1):
        if stop_event.is_set():
            break

        padded_str = f"{number:010d}"
        current_hash = hashlib.md5(padded_str.encode('utf-8')).hexdigest()
        if current_hash == target_hash:
            found_answer = padded_str
            print(f"match found: {found_answer}!")
            stop_event.set()
            break


"""
Connects to the central server, detects available CPU cores, requests range assignments,
and distributes hash cracking tasks across parallel worker threads until a match is found or work stops.
"""
def start_client():
    global stop_event, found_answer
    cores_count = os.cpu_count()
    if not cores_count:
        cores_count = 1

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))
        while not stop_event.is_set():
            request_payload = f"GET_WORK:{cores_count}"
            client_socket.sendall(request_payload.encode('utf-8'))
            raw_response = client_socket.recv(1024)
            if not raw_response:
                break
            response_text = raw_response.decode('utf-8')
            if response_text == "STOP" or response_text == "NO_MORE_WORK":
                stop_event.set()
                break

            if response_text.startswith("RANGE"):
                parts = response_text.split(":")
                start_range = int(parts[1])
                end_range = int(parts[2])
                if len(parts) >= 4:
                    target_hash = parts[3].lower()
                else:
                    target_hash = "ec9c0f7edcc18a98b1f31853b1813301".lower()

                found_answer= None
                threads_list = []

                total_numbers = end_range - start_range + 1
                chunk_size = total_numbers // cores_count

                current_start = start_range
                for i in range(cores_count):
                    # Distribute remainders to the final thread chunk
                    if i == cores_count - 1:
                        current_end = end_range
                    else:
                        current_end = current_start + chunk_size - 1

                    worker_thread = threading.Thread(
                        target=md5_worker,
                        args=(current_start, current_end, target_hash)
                    )
                    threads_list.append(worker_thread)
                    worker_thread.start()
                    current_start = current_end + 1

                for t in threads_list:
                    t.join()

                if found_answer:
                    finish_payload = f"FOUND:{found_answer}"
                    client_socket.sendall(finish_payload.encode('utf-8'))
                    stop_event.set()
                    break

    except ConnectionRefusedError:
        print("Connection rejected. Verify server status and firewall rules.")
    except socket.error as network_error:
        print(f"Low level pipeline data transmission failure: {network_error}")
    except Exception as runtime_fault:
        print(f"Client environment collapsed due to anomalous runtime event: {runtime_fault}")
    finally:
        print("Reclaiming system memory. Dismantling networking socket.")
        client_socket.close()


if __name__ == "__main__":
    start_client()
