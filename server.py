#server

import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import ast

import json #jaaaaaaaaaaaason
import math
import socket
import select
import io
import helper_client as hc
import sys
from time import sleep

# starting code

REDBC = '\033[41m'
NRMBC = '\033[49m'


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # Create a socket object
host = socket.gethostname() # Get local machine name
buffer = 4096
connections = []
public_keys = {}

pms_to_send = {}

try:
    port = int(sys.argv[1])
except:
    port = 5757

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # sets options for the server
server_socket.bind(("0.0.0.0", port)) # bind to local machine
server_socket.listen(10) # listen 10 seconds for a connection

publicfile = {"keys": {}, "names":{}}
public_keys = publicfile["keys"]
names = {}

# Add server socket to the list of readable connections
connections.append(server_socket)
print("Chat server on port " + str(port) + " .   Host: " + str(host))


while True:

    read_sockets, write_sockets, error_sockets = select.select(connections, [], [])

    for sock in read_sockets:

        # In case of a new connection
        if sock == server_socket:
            # Handle the case in which there is a new connection recieved through server_socket
            tsock, addr = server_socket.accept()
            connections.append(tsock)
            print("Client " + str(addr) + " connected")

            try:
                tsmg = "<" + str(names[str(addr[1])] + "> has entered the chatroom.\n")
            except:
                tsmg = "<" + str(addr[1]) + "> has entered the chatroom.\n"
            hc.broadcast_data("sentinelkey", "smsg", tsmg, connections, server_socket)
            sleep(0.03)
        # If sock != serve    print(message)r_socket, some incoming message or something idk
        else:

            try:
                if names[str(sock.getpeername()[1])] == "":
                    names[str(sock.getpeername()[1])] = str(sock.getpeername()[1])
            except:
                names[str(sock.getpeername()[1])] = str(sock.getpeername()[1])

            #Data recieved from client. Must process.
            try:
                # Connections can just fuck up sometimes. Who cares? Try catch statements will save us.
                data = sock.recv(buffer)
                ispmsg = False
                if(data[:6] == b'{pmsg}'):                                # hardest problem ever = solved
                    ispmsg = True
                    dtype, person, data = hc.solve_the_dreaded_pmsg(data)
                else:                                                     # ayyy lmao
                    dtype, data = hc.chipfortype(data)

                if data:
                    if dtype == "msg":
                        hc.broadcast_data(sock, "msg", "\r <" + names[str(sock.getpeername()[1])] + "> " + data, connections, server_socket)
                        sleep(0.05)

                    elif dtype == "pmsg":

                        try:
                            person = int(person) # person is the key, not the name.

                            is_valid_person = False
                            for socketToWhomYouSendTheMessage in connections:
                                if socketToWhomYouSendTheMessage != server_socket and socketToWhomYouSendTheMessage.getpeername()[1] == person:
                                    is_valid_person = True

                            if is_valid_person:
                                pms_to_send[person] = [data, sock]
                            else:
                                sock.send(bytes("{smsg} Im sorry, but this person doesn't exist!"))
                                sleep(0.03)
                        except Exception as e:
                            print(str(person) +  "   Exception thrown at ~L100:  " + str(e))
                            sock.send(bytes("{smsg} Hey, you need to enter people id's, not their name! Use !lsids {name} to find their id.\n", "utf-8"))
                            sleep(0.03)

                    elif dtype == "keyset":
                        their_public_key = data
                        public_keys[str(sock.getpeername()[1])] = their_public_key

                    elif dtype == "keyreq":
                        tip = data.replace("\n", "")
                        try:
                            their_public_key = public_keys[tip]
                            sock.send(bytes("{pubkey}{"+str(tip)+"}"+their_public_key, "utf-8"))
                            sleep(0.02)
                        except:
                            print("attempted to get pubkey of " + tip + "  but failed..")
                            sock.send(bytes("{error}That key doesn't exist! (A key was requested that didn't exist.)", "utf-8"))
                            sleep(0.02)

                    elif dtype == "newname":
                        names[str(sock.getpeername()[1])] = data

                    elif dtype == "lsids":
                        possibles = "People named "+data[:-1]+" : \n"
                        for sid in names:
                            # print("SID : " + sid)
                            if names[sid] == data[:-1]:
                                possibles += "\t  - " + str(sid)

                        sock.send(bytes("{smsg}" + possibles + "\n", "utf-8"))
                        sleep(0.02)

                if data == "":
                    connections.remove(sock)
                    print(REDBC + str(sock.getpeername()) + " disconnected\n" + NRMBC)
                    hc.broadcast_data(sock, "smsg", "User <" + names[str(sock.getpeername()[1])] + "> has logged off.\n", connections, server_socket)
                    sleep(0.02)

            except Exception as e:
                hc.broadcast_data(sock, "smsg", "Client " + str(addr) + " has disconnected.\n", connections, server_socket)
                sleep(0.02)
                print("User has been forcefully disconnected")
                print(REDBC + " ERROR: " + str(e) + NRMBC)
                sock.close()
                connections.remove(sock)
                continue

    for sock in connections:
        if sock != server_socket:
            should_pop = []
            for pm in pms_to_send:
                try:
                    if str(sock.getpeername()[1]) == str(pm):
                        sleep(0.04)

                        print("sending pm to " + str(pm) + " from " + str(sock.getpeername()[1]))
                        personsname = "<" + str(pms_to_send[pm][1].getpeername()[1]) + "> "
                        sock.send(bytes("{pmsg}" + "{" + personsname + "}", "utf-8") + pms_to_send[pm][0])
                        sleep(0.02)

                        pms_to_send[pm][1].send(bytes("{smsg} Correctly sent the message to " + str(pm) + "\n", "utf-8"))
                        sleep(0.02)
                        should_pop.append(pm)

                except Exception as ee:
                    print("sent error")
                    pms_to_send[pm][1].send(bytes("{smsg} Error sending message to " + str(pm) + "\n", "utf-8"))
                    sleep(0.02)
                    print(str(ee))

            for pm in should_pop:
                pms_to_send.pop(pm)

server_socket.close()
