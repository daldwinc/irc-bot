#!/usr/bin/python3
# Bot framework by Linux Academy at https://github.com/Orderchaos/LinuxAcademy-IRC-Bot

import socket
import requests
import json
import datetime
import time

#irc basics
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#load config
with open('config.json', 'r') as f:
    config = json.load(f)

server = config['server']
channel = config['channel']
botnick = config['botnick']
adminname = config['adminname']
exitcode = config['exitcode']

ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667
ircsock.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick + " " + botnick + "\n", "UTF-8")) # user information
ircsock.send(bytes("NICK "+ botnick +"\n", "UTF-8")) # assign the nick to the bot

#API setup
#blockchair API
blockchair_base = 'https://api.blockchair.com/bitcoin/'
blockchair_headers = {'Content-Type': 'application/json'}
#blockchain API
blockchain_base = 'https://blockchain.info/'
blockchain_headers = {'Content-Type': 'application/json'}


#irc functions
def joinchan(chan): # join channel(s).
  ircsock.send(bytes("JOIN "+ chan +"\n", "UTF-8")) 
  ircmsg = ""
  while ircmsg.find("End of /NAMES list.") == -1: 
    ircmsg = ircsock.recv(2048).decode("UTF-8")
    ircmsg = ircmsg.strip('\n\r')
    print(ircmsg)

def login():
  ircsock.send(bytes("PRIVMSG "+ "NickServ" +" :"+ "IDENTIFY thebotpassword" +"\n", "UTF-8"))

def ping(): # respond to server Pings.
    ircsock.send(bytes("PONG :pingis\n", "UTF-8"))

def sendmsg(msg, target=channel): # sends messages to the target.
  ircsock.send(bytes("PRIVMSG "+ target +" :"+ msg +"\n", "UTF-8"))


#trigger functions
def tslb():
    api_url = '{0}latestblock'.format(blockchain_base)
    r = requests.get(api_url, headers=blockchain_headers)
    if r.status_code == 200:
        d = json.loads(r.content.decode('UTF-8'))
        if d is not None:
            last_time = int(d['time'])
            current_time = int(time.time())
            time_diff = current_time - last_time
            seconds_to_time = str(datetime.timedelta(seconds=time_diff))
            sendmsg("Time elapsed since last block: " + seconds_to_time)
        else:
            print('[!] Command failed.')
    else:
        print('[!] Command failed.')


def main():
  login()
  
  while 1:
    ircmsg = ircsock.recv(2048).decode("UTF-8")
    ircmsg = ircmsg.strip('\n\r')
    print(ircmsg)

    if ircmsg.find("PRIVMSG") != -1:
      name = ircmsg.split('!',1)[0][1:]
      message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]
      if len(name) < 17:
        
       ##################################################################
       # Commands go here

        if message[:5].find('!help') != -1:
          sendmsg("Command List:", name)
          sendmsg('!help      - Show this list', name)
          sendmsg('!tslb       - Print time of last block', name)
          sendmsg('!losers    - Print names of idiots to channel', name)
          sendmsg('!join    - attempt to channel', name)
        
        if message[:7].find('!join') != -1:
          joinchan(channel)

        if message[:7].find('!losers') != -1:
          sendmsg("Roger Ver, Craig Wright, Calvin Ayr")

        if message[:5].find('!tslb') != -1:
          tslb()

      # Commands end
      ##################################################################
       
      #kill function
      if name.lower() == adminname.lower() and message.rstrip() == exitcode:
        sendmsg("oh...okay. :'(")
        ircsock.send(bytes("QUIT \n", "UTF-8"))
        return
    else:
      if ircmsg.find("PING :") != -1:
        ping()
main()
