#client http://www.binarytides.com/code-chat-application-server-client-sockets-python/ reference

import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import ast

from helper_client import chipfortype
import helper_client as hc
import json
import math
import socket, select, string, sys      # Import socket module
import os
from time import sleep


random_generator = Random.new().read

def update_pub_key(key):
    pubkey = key.publickey()
    formattedpubkey = pubkey.exportKey("PEM")
    #print(formattedpubkey.decode("utf-8"))
    s.send(bytes("{keyset}" + formattedpubkey.decode("utf-8"), "utf-8"))

# send a request for a public key
def get_public_key(ip):
    s.send(bytes("{keyreq}"+str(ip), "utf-8"))

def make_keys():
    random_generator = Random.new().read
    key = RSA.generate(1024, random_generator) #generate pub and priv key
    return key

#save the public keys
def p_save_keys(ddata):
    ndata = json.dumps(ddata, indent=4, sort_keys=True)
    privfile.seek(0)
    privfile.truncate()
    privfile.write(ndata)


def prompt():
    sys.stdout.write("   <" + myname + ">: ")
    sys.stdout.flush()


#load the public keys
def p_load_keys():
    data = privfile.read().replace('\n', '')
    return json.loads(data)

#save the public keys
def p_save_keys(ddata):
    ndata = json.dumps(ddata, indent=4, sort_keys=True)
    privfile.seek(0)
    privfile.truncate()
    privfile.write(ndata)


s = socket.socket()                     # Create a socket object
host = s.getsockname()[0]                 #socket.gethostname() # Get local machine name
port = 5757                             # Reserve a port for your service.
encoding = 'utf-8'
myname = "YOU"
privdata = {}
my_key = ""

everyones_public_keys = {}

name_update_needed = True

GRNC = '\033[1;32m'
NRMC = '\033[0m'
LGRYC = '\033[0;37m'
WHTC = '\033[1;37m'
REDC = '\033[0;31m'
LREDC = '\033[1;31m'
DGRNC = '\033[0;32m'
REDBC = '\033[41m'
NRMBC = '\033[49m'
YLWBC = '\033[43m'
MAGC = '\033[38;5;85m'

alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
 "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
 "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N",
 "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

privfile = open("private_shit.json", "r+")

try:
    privdata = p_load_keys()
    myname = privdata["myname"]
    name_update_needed = True
except:
    print(YLWBC+"Either it's your first time here, or your local file broke, or you're running more than one client on your machine. Should I set up the defaults?"+NRMBC)
    yn = input("[Y/n] : ")
    if yn != "Y":
        print("Adios!")
        exit()
    myname = "YOU"
    privdata["myname"] = str(myname)

    try:
        p_save_keys({"myname": myname})
    except:
        print(YLWBC+"Cannot save options, maybe the file is in use?"+NRMBC)

ppmsg = ""
pmsg = ""
should_print_pub_keys = False

#main function
if __name__ == "__main__":

    if (len(sys.argv) < 3) :
        print("Usage : client.py {hostname} {port} [fakeinputfile]")
        sys.exit()

    host = sys.argv[1]
    port = int(sys.argv[2])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    if len(sys.argv) >= 4:
        fake_input = sys.argv[3]
        sys.stdin = open(fake_input)

    #connections
    try:
        s.connect((host, port))
    except:
        print (REDC + "Unable to connect" + NRMC)
        sys.exit()

    print(GRNC + "Connected to remote host. Start sending messages" + NRMC)
    prompt()

    my_key = make_keys()
    update_pub_key(my_key)

    while 1:
        socket_list = [sys.stdin, s]

        #Get the list of sockets which are accesssible
        read_sockets = read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

        for sock in read_sockets:

            sleep(0.005)

            #incoming message from remote server
            if sock == s:
                data = sock.recv(4096)
                if data[:6] == b'{pmsg}':
                    dtype, person, data = hc.solve_the_dreaded_pmsg(data)
                    data = data[1:]
                else:
                    dtype, data = chipfortype(data) # seperates raw data into datatype and data

                if not data:
                    print(REDC + '\nDisconnected from chat server' + NRMC)
                    sys.exit()
                else :
                    #print data
                    if dtype == "msg":
                        sys.stdout.write(LGRYC + data + NRMC)
                    elif dtype == "pmsg":
                        #print("before decrypt")
                        #print(data)
                        data = my_key.decrypt(data)
                        #print("after decrypt")
                        #print(data)
                        sys.stdout.write("\n" + MAGC + person + data.decode("utf-8") + NRMC)
                    elif dtype == "smsg":
                        sys.stdout.write("\n"+ GRNC + " --> SERVER: " + data + NRMC)
                    elif dtype == "cls":
                        os.system("clear")
                        sys.stdout.write(data)
                    elif dtype == "error":
                        sys.stdout.write(REDBC + data + NRMC)
                    elif dtype == "pubkey":
                        person, data = chipfortype(data, isbytes=False)
                        everyones_public_keys[person] = data
                        print("Recieved publickey for pId: " + person)

                    prompt()

            #user entered a message
            else:
                msg = sys.stdin.readline()
                if msg == "!leaveserver\n":
                    sys.exit()

                elif msg == "!leavechatroom\n":
                    # TODO
                    pass

                elif msg == "!help\n":
                    print(DGRNC+"\t|"+GRNC+"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"+DGRNC+"|")
                    print(DGRNC + "\t|             "+GRNC+"~~ APSM Ver 1.2 ~~"+DGRNC+"            |")
                    print("\t|                                           |")
                    print("\t|   Type into the chat channel and press    |")
                    print("\t|          enter to send a message.         |")
                    print("\t| Some messages have special meanings, like |")
                    print("\t|    the one you just entered. They are     |")
                    print("\t| almost always prefixed with the '!' key.  |")
                    print("\t|                                           |")
                    print("\t|"+GRNC+"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"+DGRNC+"|")
                    print("\t|                                           |")
                    print("\t|   Perhaps you'd want a name. Just type:   |")
                    print("\t|     " + GRNC + "   !name {name} " + DGRNC + " to set a name        |")
                    print("\t|                                           |")
                    print("\t|   For more helpful commands, type "+GRNC+"!cmds"+DGRNC+"   |")
                    print("\t|                                           |")
                    print("\t|                   "+GRNC+"Adios!"+DGRNC+"                  |")
                    print("\t|"+GRNC+"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"+DGRNC+"|")
                    print(NRMC)
                    #atast500dmoo2-1bd14
                elif msg == "!clear\n":
                    os.system("clear")

                elif msg == "!cmds\n":
                    print(DGRNC+"\t|"+GRNC+"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"+DGRNC+"|")
                    print(DGRNC + "\t|                "+GRNC+"~~ APSM Ver 1.2 ~~"+DGRNC+"               |")
                    print("\t|  > !name {name} -sets the name of the client    |")
                    print("\t|  > !OS {commands} -executes commands through    |")
                    print("\t| . the operating system / command line           |")
                    print("\t|  > !leaveserver -exits the application.         |")
                    print("\t| . this is reccomended over ctrl+C               |")
                    print("\t|  > !printpublickey -prints your public key      |")
                    print("\t|  > !lsids {name} -lists the possible            |")
                    print("\t| . server id's for a name. See !lsall.           |")
                    print("\t|  > !lsall -lists all the people connected to    |")
                    print("\t| . the server at that time, id, then name.       |")
                    print("\t|  > !pm {pId} {message} -attempts to pm the id   |")
                    print("\t| . supplied by pId. To get id's from names,      |")
                    print("\t| . use !lsids {name} .                           |")
                    print("\t|  > !getpubkey {pId} -attempts to get the public |")
                    print("\t| . key belonging to {pId}.                       |")
                    print("\t|  > !cls  -shortcut for !OS clear/cls            |")
                    print("\t|"+GRNC+"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"+DGRNC+"|")
                    print(NRMC)

                elif msg[:4] == "!cls":
                    os.system("clear")

                elif msg[:10] == "!getpubkey":
                    #print("--Attempting to get public key--")
                    args = msg.split(' ')
                    get_public_key(args[1])
                    should_print_pub_keys = True

                elif msg[:3] == "!pm":
                    args = msg.split(' ')
                    args.pop(0)
                    pId = args.pop(0)
                    tdata = ' '.join(args)
                    try:
                        theirpubkey = everyones_public_keys[pId]
                        theirpubkeyobj = RSA.importKey(theirpubkey)
                        tdatae = theirpubkeyobj.encrypt(bytes(tdata, "utf-8"), "x")[0]
                        #print(tdatae)
                        s.send(bytes("{pmsg}{" + pId + "} ", "utf-8") + tdatae)
                    except ValueError as e:
                        print("Your message may have been too long. Please, try again.")
                    except Exception as e:
                        print("Couldn't find their public key. Are you sure you have it?")
                        print("You can force it to update with !getpubkey {pId}")

                elif msg[:6] == "!lsids":
                    try:
                        name = msg.split(' ')[1]
                        s.send(bytes("{lsids}"+name, "utf-8"))
                    except IndexError:
                        print(REDC+" Usage: !lsids {name}"+NRMC)

                elif msg[:3] == "!OS":
                    temp = msg.split(' ')
                    temp.pop(0)
                    os.system(' '.join(temp))

                elif msg[:5] == "!name":
                    myname = msg.split(' ')[1].replace('\n', '')

                    firstLetterIsAlphabetical = False
                    for letter in alphabet:
                        if myname[0] == letter:
                            firstLetterIsAlphabetical = True
                            break

                    if(len(myname) > 15):
                        print("Name too long!  You tried: " + myname)
                    elif (len(myname) < 2):
                        print("Name too short!  You tried: " + myname)
                    elif firstLetterIsAlphabetical:
                        # print("Name just right!") # geddit, like goldilocks and the three bears? #PolymorphicProgrammingMeme
                        s.send(bytes("{newname}"+myname, "utf-8"))
                    else:
                        print("First letter must be alphabetical!")

                elif msg == "!printpublickey\n":
                    print(my_public_key)

                else:
                    s.send(bytes("{msg}" + msg, "utf-8"))

                    if (pmsg == msg and ppmsg == msg):
                        print(REDBC + " P L E A S E   N O   S P A M " + NRMBC)
                        exit()

                    ppmsg = pmsg
                    pmsg = msg
                prompt()

            sleep(0.01)
            p_save_keys({"myname": myname})
            if name_update_needed:
                s.send(bytes("{newname}"+myname, "utf-8"))
                name_update_needed = False
