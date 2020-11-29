import socket
import pickle
import json
import requests
import threading
import random
from datetime import datetime

# Set the header to 69 just for the connotation
HEADER = 2048
PORT = 12345
FORMAT = 'utf-8'

#user_list = []
active_users = []
bronze_users = []
silver_users = []
gold_users = []

games = []

GET_USERS_API = "https://rrnkqflue2.execute-api.us-east-1.amazonaws.com/default/GetUser"
UPDATE_USERS_API = "https://a39iscukd1.execute-api.us-east-1.amazonaws.com/default/UpdateUser"

# helpful utility functions
# Sends a message to a client
def SendMsg(msg, c):
    msg = json.dumps(msg)
    c.send(bytes(msg,FORMAT))
# Recieves a message from client
def RecieveMsg():
    global server_socket
    msg = server_socket.recv(HEADER).decode(FORMAT)
    if msg:
        msg = json.loads(msg)
        return msg

#gets all registered users from dynamoDB
def GetUsers():
    r = requests.get(GET_USERS_API)
    rjson = r.json()
    return rjson['Items']
#gets a specific registered user from dynamoDB
def GetUser(id):
    user_list =  GetUsers()
    for u in user_list:
        if u['id'] == id:
            return u
    return None

# updates the users in the dynamodb
def UpdateUsers(updatedUsers):
    users =  GetUsers()
    for old in users:
        for new in updatedUsers:
            if old['id'] == new['id']:
                old = new
    for user in users:
        if int(user['skill']) < 25:
            user['tier'] == 'bronze'
        elif int(user['skill']) > 25 and int(user['skill']) <=75:
            user['tier'] == 'silver'
        elif int(user['skill']) < 75:
            user['tier'] == 'gold'
    msg = {'Items':users}
    requests.post(UPDATE_USERS_API,msg)
    

# helper function for SortActiveUsers()
def hTier(v):
    return v['tier']

#sorts the active users list by tier
def SortUsers(users):
    users.sort(reverse=False,key=hTier)
    for user in users:
        if user['tier'] == 'bronze':
            bronze_users.append(user)
        elif user['tier'] == 'silver':
            silver_users.append(user)
        elif user['tier'] == 'gold':
            gold_users.append(user)

def FindPlayer(ul,pl):
    for u in ul:
        if u not in pl:
            return u
        



def SimulateGame(user,guess,conn):
    SortUsers(GetUsers())
    number = random.randint(1,10)
    u_users = []
    p_users = [user]
    players = [{'player':user,'guess':guess}]
    if user['tier'] == 'bronze':
        for o in range(2):
            p_guess = random.randint(0,10)
            canidate = FindPlayer(bronze_users,p_users)
            p_users.append(canidate)
            players.append({'player':canidate, 'guess':p_guess}) 
    elif user['tier'] == 'silver':
        for o in range(2):
            p_guess = random.randint(0,10)
            canidate = FindPlayer(silver_users,p_users)
            p_users.append(canidate)
            players.append({'player':canidate, 'guess': p_guess})  
    elif user['tier'] == 'gold':
        for o in range(2):
            p_guess = random.randint(0,10)
            canidate = FindPlayer(gold_users,p_users)
            p_users.append(canidate)
            players.append({'player':canidate, 'guess': p_guess})  
            
    if len(players) == 3:
        log = open('game.log','a')
        t = datetime.now()
        start_time = t.strftime("%m/%d/%Y, %H:%M:%S")
        log.write(f"Game started at: {start_time} Players: {players} \n")
        log.close()
        players.sort(reverse=True,key=rank)
        rankings = f"The number was: {number}"
        #first place
        rankings += f"\n 1st place: {players[0]} skill + 2"
        oldSkill = int(players[0]['player']['skill'])
        newSkill = oldSkill + 2
        players[0]['player']['skill'] = str(newSkill)
        #second place
        rankings += f"\n 2nd place: {players[1]} skill + 1"
        oldSkill = int(players[1]['player']['skill'])
        newSkill = oldSkill + 1
        players[1]['player']['skill'] = str(newSkill)
        #third place
        rankings += f"\n 3rd place: {players[2]}"
        SendMsg({'EVENT':'results','RANKS':rankings},conn)
        log = open('game.log','a')
        t = datetime.now()
        start_time = t.strftime("%m/%d/%Y, %H:%M:%S")
        log.write(f"Game ended at: {start_time} Players: {players} \n")
        log.close()
        for i in range(3):
            u_users.append(players[i]['player'])
    UpdateUsers(u_users)
    
def rank(p):
    return [p['guess']]      
        
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((socket.gethostname(),PORT))

SortUsers(GetUsers())


def handleClient(connection, address):
    print(f"client with address: {address} has connected")
    connected = True
    while connected:
        msg = connection.recv(HEADER).decode(FORMAT)
        if msg:
            msg = json.loads(msg)
            if msg['EVENT'] == 'logout':
                connected = False
                active_users.remove(msg['USER'])
                connection.close()
            elif msg['EVENT'] == 'login':
                if GetUser(msg['ID']) == None:
                    SendMsg({'EVENT':'decline','MSG':'The User you typed does not exist.'},connection)
                else:
                    user = GetUser(msg['ID'])
                    active_users.append(user)
                    log = open('game.log','a')
                    log.write(f"{user} has logged in at {datetime.now()} \n")
                    log.close()
                    print(f"users currently logged in: {active_users}")
                    SendMsg({'EVENT':'accept', 'USER_DATA': user},connection)
            elif msg['EVENT'] == 'play':
                SimulateGame(msg['USER'],msg['GUESS'],connection)
            else:
                SendMsg({'EVENT':'wait'},connection)                       
    connection.close()

def Start():
    server_socket.listen()
    print(f"Listening...")
    while True:
        client, address = server_socket.accept()
        thread = threading.Thread(target=handleClient, args=(client,address))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("Starting server...")
Start()