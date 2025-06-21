import socket
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--host", type=str, required=True)
parser.add_argument("--port", type=int, required=True)
parser.add_argument("--token", type=str, required=True)
parser.add_argument("--folder", type=str)

args = parser.parse_args()
os.makedirs(args.folder, exist_ok=True)

def connect_to_master():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((args.host, args.port))
        print(f"[WORKER] connected to {args.host}")
        sock.sendall(args.token.encode())
        print(f"[WORKER] sent token to master")
        while True:
            header = sock.recv(1024).decode()
            if not header:
                break
            if header.startswith("[FILE]::"):
                try:
                    parts = header.strip().split("::")
                    filename = parts[1]
                    length = int(parts[2])
                    filepath = os.path.join(args.folder, filename)
                    print(f"[INFO] Receiving {filename} ({length} bytes)")
                    # how many bytes have been received
                    received = 0
                    # collect small pieces of file
                    chunks = []
                    while received < length:
                        # should not receive more than 4096 
                        chunk = sock.recv(min(4096, length - received))
                        if not chunk:
                            break
                        # append to chunks and add to received
                        chunks.append(chunk)
                        received += len(chunk)
                    # write binary from chunks to a file
                    with open(filepath, "wb") as f:
                        f.write(b"".join(chunks))

                except Exception as e:
                    print(f"[ERROR] Parsing file header or writing: {e}")
            elif header.startswith("[DELETE]::"):
                try:
                    parts = header.strip().split("::")
                    filename = parts[1]
                    filepath = os.path.join(args.folder, filename)
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        print(f"[DELETED] {filename} removed from worker folder")
                    else:
                        print(f"[INFO] {filename} already missing, no action taken")
                except Exception as e:
                    print(f"[ERROR] couldn't delete {filename}")
            else:
                print(f"[MASTER → WORKER] {header}")
    except Exception as e:
        print(f"[ERROR] Could not connect or communicate with master: {e}")

    finally:
        sock.close()
        print("[WORKER] Disconnected.")

if __name__ == "__main__":
    connect_to_master()
