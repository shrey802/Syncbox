
# 🔄 SyncBox

> A lightweight, secure, LAN-based file sync tool — built in Python over a weekend.

SyncBox is a CLI tool that syncs files and deletions in real-time between a **master device** and one or more **worker devices** over LAN using sockets and file system watchers.

It mimics the core functionality of Dropbox — but for your **local network**, without the cloud.

---

## 🚀 Features

| Feature                      | Status | Description |
|-----------------------------|--------|-------------|
| 🔌 LAN-based file transfer   | ✅     | TCP/IP over local network |
| 📁 Watch folder for changes  | ✅     | Uses `watchdog` to detect file events |
| 🔐 Token-based auth          | ✅     | One-line security to block unknown workers |
| 🖥 CLI-based config          | ✅     | Simple `argparse` usage |
| 🔄 Real-time sync            | ✅     | Syncs new & updated files instantly |
| ❌ File deletion sync        | ✅     | Deletes removed files on all devices |
| 🧾 Minimal logging output    | ✅     | Clear CLI messages |

---

## 🛠 Requirements 

1) python environment

2) pip install watchdog

## 📁 Project Structure

master.py -> Master file

worker.py -> Worker file

sync_master -> folder for master

sync_worker -> folder for worker

## 💻 Usage

For master.py Run 

``` python3 master.py --port 9999 --folder sync_master --token secret123 ```

For worker.py Run

``` python3 worker.py --host 127.0.0.1 --port 9999 --token secret123 --folder sync_worker ```


![syncbox_deletio![syncbox_text](https://github.com/user-attachments/assets/1fabd1f6-a492-4e3b-8244-c4c788c0cf57)


![syncbox](https://github.com/user-attachments/assets/0f6205c7-c862-40c4-ae51-f5730f19f888)


![syncbox](https://github.com/user-attachments/assets/60b3df92-1a9b-4636-a7d1-8b913963bb71)



