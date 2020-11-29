import socket
import select
import json
import requests

HEADER = 2048
PORT = 12345
IP = '54.80.57.114'
FORMAT = 'utf-8'

user = {}

GET_USERS_API = "https://rrnkqflue2.execute-api.us-east-1.amazonaws.com/default/GetUser"
UPDATE_USERS_API = "https://a39iscukd1.execute-api.us-east-1.amazonaws.com/default/UpdateUser"

#-------------------------------------Helpful functions-------------------------------------

# sends message and gets response from server
def SendMsg(msg):
    msg = json.dumps(msg)
    client_socket.send(bytes(msg,FORMAT))

def RecieveMsg():
    global client_socket
    msg = client_socket.recv(HEADER).decode(FORMAT)
    if msg:
        msg = json.loads(msg)
        return msg

client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((IP,PORT))

#

running  = True

def Gameplay():
    game_event = RecieveMsg()
    while game_event['EVENT'] != 'results':
        game_event = RecieveMsg()
    print(game_event['RANKS'])
    
while running:
    print("Welcome To The Number Guessing Game!")
    id = input('what is your ID? \n')
    SendMsg({'EVENT':'login','ID': id})
    msg = RecieveMsg()
    if msg['EVENT'] == 'accept':
        user = msg['USER_DATA']
        print(msg['USER_DATA'])
        print("1. connect to a game")
        print("2. quit")
        cmd = input("What do you want to do? \n")
        if cmd == '1':
            n = int(input("how many games do you want to play? \n"))
            for g in range(n):
                guess = int(input('Guess a number betweeen 1 and 10 \n'))
                SendMsg({'EVENT': 'play','USER':user,'GUESS':guess})
                Gameplay()
        elif cmd == '2':
            SendMsg({'EVENT': 'logout', 'USER': user})
            running = False
    elif msg['EVENT'] == 'decline':
        print(msg['MSG'])