import json
from random import randint


import sys
from time import sleep
from threading import Thread

shutterFrames = ["\\", "|", "/", "-"]
class loadingShutter(Thread):
    def run(self):
        i = 0
        while True:
            sys.stdout.write(shutterFrames[i])
            sys.stdout.flush()
            sleep(0.5)
            sys.stdout.write("\b")
            i += 1
            i %= 4

def solve_the_dreaded_pmsg(data):
    xarr = data.split(b'}', 2)
    return xarr[0].decode("utf-8").replace("{", ""), xarr[1].decode("utf-8").replace("{", ""), xarr[2]

def chipfortype(data, isbytes=True):
    dtype = ""
    if isbytes:
        data = data.decode("utf-8")
    ndata = ""
    has_started = False
    has_finished = False

    for char in data:
        if has_started and has_finished:
            ndata += char
        elif char == "{":
            has_started = True
            continue
        elif char == "}" and has_started:
            has_finished = True
        elif has_started:
            dtype += char

    if ndata != "":
        data = ndata

    return dtype, data


# access public keys
## TODO
def get_public_keys(ip):
    return 12345689

# send a message returns true if successful
## TODO
def send_message(ip):
    return True

# create a public key return persons ip
## TODO
def generate_public_key():
    key = ""
    for i in range (0, 256):
        key += str(randint(0, 1))
    return key

def broadcast_data (s, dtype, message, connections, server_socket):
    #Do not send the message to master socket and the client who has send us the message

    print("(TO ALL) " + message)
    message = "{" + dtype + "}" + message

    for socket in connections:
        if socket != server_socket and socket != s :
            try :
                socket.send(bytes(message, "utf-8"))
            except :
                # broken socket connection may be, chat client pressed ctrl+c for example
                print("Dude dead lol")
                socket.close()
                connections.remove(socket)
