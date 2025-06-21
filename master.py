import socket
import argparse
import threading
from watchdog.observers import Observer
import os
import time
from watchdog.events import FileSystemEventHandler

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, required=True)
parser.add_argument("--folder", type=str, required=True)
parser.add_argument("--token", type=str, required=True)

args = parser.parse_args()

connected_workers = []

def start_server():
    # creating a server socket and AF_INET is IPv4 address, and SOCK_STREAM is stream based not datagram based so TCP not UDP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind worker connections to the port specified and get from all networks 0.0.0.0 is special IP
    server_socket.bind(('0.0.0.0', args.port))
    # allow 5 connections simultaneously
    server_socket.listen(5)
    print(f"[MASTER] Listening on port {args.port}...")
    while True:
        # client_socket is object after connection and client_addr is IP and port of client
        client_socket, client_addr = server_socket.accept()
        threading.Thread(target=handle_worker, args=(client_socket, client_addr)).start()


def handle_worker(sock, addr):
    try:
        # recieve upto 1024 bytes of data and decode turns bytes to string and then use strip for whitespaces
        token = sock.recv(1024).decode().strip()
        if token != args.token:
            print(f"[REJECTED] {addr} provided invalid token.")
            sock.close()
            return
        
        print(f"[ACCEPTED] {addr} connected.")
        connected_workers.append({"socket": sock, "address": addr})
    except Exception as e:
        print(f"[ERROR] Worker {addr} crashed", e)
        sock.close()


class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        filepath = event.src_path
        print(f"[WATCHDOG] file modified: {filepath}")
        send_to_workers(filepath)

    def on_created(self, event):
        if event.is_directory:
            return
        filepath = event.src_path
        print(f"[WATCHDOG] file created: {filepath}")
        send_to_workers(filepath)

    def on_deleted(self, event):
        if event.is_directory:
            return
        filename = os.path.basename(event.src_path)
        print(f"[WATCHDOG] file deleted: {filename}")
        notify_deletion_to_workers(filename)

def send_to_workers(filepath):
    try:
        filename = os.path.basename(filepath)
        with open(filepath, "rb") as file:
            content = file.read()
        header = f"[FILE]::{filename}::{len(content)}".encode()
        for worker in connected_workers:
            try:
                worker['socket'].sendall(header)
                time.sleep(0.1)
                worker['socket'].sendall(content)
            except Exception as e:
                print(f"[ERROR] sending to {worker['address']} {e}")
    except Exception as e:
        print("Exception occured", e)
        return


def notify_deletion_to_workers(filename):
    message = f"[DELETE]::{filename}".encode()
    for worker in connected_workers:
        try:
            worker['socket'].sendall(message)
            print(f"[NOTIFY] Sent delete command for {filename} to {worker['address']}")
        except Exception as e:
            print(f"Couldn't notify workers: {e}")


def start_watcher():
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=args.folder, recursive=False)
    observer.start()
    print(f"[WATCHDOG] Watching folder: {args.folder}")


if __name__ == "__main__":
    threading.Thread(target=start_watcher, daemon=True).start()
    start_server()