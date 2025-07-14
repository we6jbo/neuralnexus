#!/usr/bin/env python3
import threading
import requests
import time
import queue
import subprocess
import datetime
import hashlib
import threading
import time
import paramiko
import re
import signal
import sys
import requests
from duckpy import Client

# Global values added by joneal
slowAI = 0 
slowSSH = 0 

# ==== Configuration ====
ZORK_HOST = "192.168.7.120"
ZORK_USER = "jeremiah"
ZORK_COMMAND = "zork"  # Optional if used

# ==== Global State ====
command_queue = queue.Queue()
ssh_client = None
shell = None

# ==== Signal Handling ====
def signal_handler(sig, frame):
    print("\n[!] Exiting...")
    if ssh_client:
        ssh_client.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# ==== SSH Setup ====
def init_ssh():
    global ssh_client, shell
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ZORK_HOST, username=ZORK_USER)
        shell = ssh_client.invoke_shell()
        shell.send("./joneal97m.sh\n")
        ai_suggest("Hello")
        print("[+] SSH session established.")
    except Exception as e:
        print("[!] SSH connection failed:", e)
        sys.exit(1)

# ==== SSH Thread ====
def ssh_handler():
    global slowSSH, slowAI
    if slowSSH > 2: 
        slowSSH = slowSSH - 1
    while True:
        if slowSSH < 2:
            slowSSH = slowSSH + 1
        if slowAI > slowSSH:
            slowSSH = slowSSH - 1
        if slowSSH < slowAI:
            slowAI = slowAI + 1
        if slowSSH > 10:
            slowSSH = 2 
        time.sleep(slowSSH) 
        slowSSH = slowSSH + 2 
        try:
            if shell and shell.recv_ready():
                output = shell.recv(4096).decode("utf-8").strip()
                print("[SSH]", output)
                command_queue.put(output)
        except Exception as e:
            print("[SSH Error]", e)
        time.sleep(1)

# ==== AI Suggestion Thread ====
def ai_handler():
    global slowAI,slowSSH
    if slowAI > 2:
        slowAI = slowAI - 1
    print("[AI Handler] Started")
    while True:
        if slowAI < 2:
            slowAI = slowAI + 1
        if slowSSH > slowAI:
            slowAI = slowAI - 1
        if slowAI < slowSSH:
            slowSSH = slowSSH + 1
        if slowAI > 10:
            slowAI = 2 
        time.sleep(slowAI)
        slowAI = slowAI + 2
        try:
            if not command_queue.empty():
                cmd = command_queue.get()
                ai_response = ai_suggest(cmd)
                if shell:
                    shell.send(ai_response + "\n")
        except Exception as e:
            print("[AI Handler Error]", e)
        time.sleep(2)

# ==== AI Request ====
def ai_suggest(user_input):
    payload = {
        "model": "llama3",
        "prompt": f"'{user_input}'",
        "stream": False
    }
    try:
        r = requests.post("http://localhost:11434/api/generate", json=payload,timeout = 30)
        return r.json().get("response", "[AI Error: No response]").strip()
    except Exception as e:
        return f"[AI Request Failed: {e}]"

# ==== Repeating Timer ====
def schedule_prompt(interval, message):
    def task():
        command_queue.put(message)
        schedule_prompt(interval, message)  # Reschedule
    threading.Timer(interval, task).start()

# ==== Start All Timers ====
def start_timers():
    schedule_prompt(699, "Respond only with learn_about lucy Ann Smith February 15 1795")   # Every 10 minutes
    #schedule_prompt(2600, "Respond only with: mindkey joneal")              # Every 45 minutes
    schedule_prompt(36, "Should I backup? Only say DO_BACKUP_NOW or NO_BACKUP_NEEDED")             # Every 1 hour


# ==== Function to allow the AI to search DuckDuckGo ====
def ai_search(query):
    try:
        client = Client()
        results = client.search(query)
        print("🔎 Top result(s):")
        for r in results[:1]:
            print("1.", r)
            command_queue.put(r)
        return results[0] if results else "No results found."
    except Exception as e:
        return f"Web search failed: {e}"

# ==== Allows the AI to backup the code to a ssh server ====

def ai_backup():
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"zorkai_{timestamp}.py"

        remote_user = "ameliahedtkealiceelliott"
        remote_host = "100.93.202.151"
        remote_path = f"{remote_user}@{remote_host}:~/{new_filename}"

        scp_command = [
            "scp",
            "/usr/local/bin/zorkai",
            remote_path
        ]

        result = subprocess.run(scp_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        command_queue.put("✅ Backup retry succeeded — no need to back up again if asked")
        return True

    except subprocess.CalledProcessError as e:
        command_queue.put("❌ Backup retry failed again. Can you enter the line again for backing up")
        print(e.stderr.decode())
        return False

    except Exception as e:
        command_queue.put("❌ Backup retry failed again I am using SCP transfer and so another backup attempt may be nessisary.")
        return False

# ==== Provides a password for the ai ====

def ai_password(user_input):
    try:
        combined = user_input + "@WT1LMs1"
        solution = hashlib.md5(combined.encode('utf-8')).hexdigest()
        command_queue.put("You are a command-driven assistant. Respond only with: glyph " + user_input + " " + "@WT" + solution[:6])
        return "@WT" + solution[:6]
    except Exception as e:
        print("[!] Error:", e)
        command_queue.put("You are a command-driven assistant. Respond only with: glyph " + user_input + " " + "@XU2MNt2")
        return "@XU2MNt2"
def ai_suggest(user_input):
    payload = {
        "model": "llama3",
        "prompt": f"{user_input}",
        "stream": False
    }
    try:
        r = requests.post("http://localhost:11434/api/generate", json=payload)
        ai = r.json().get("response", "").strip()
        print("\n🤖 AI:", ai) 
        if "do_backup_now" in ai.lower(): ai_backup()
        parts = ai.strip().split()
        if len(parts) == 2 and "mindkey" in parts[0].lower(): ai_password(parts[1])
        if "learn_about" in parts[0].lower():
            query = " ".join(ai.lower().split()[1:])
            ai_search(query)
        return ai
    except Exception as e:
        print("[!] AI error:", e)
        return "[!] AI suggestion failed"

# ==== Main Entrypoint ====
def main():
    print("\n🧙 ZorkAI Co-Pilot Initializing...")
    init_ssh()
    start_timers()
    threading.Thread(target=ssh_handler, daemon=True).start()
    threading.Thread(target=ai_handler, daemon=True).start()

    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()

