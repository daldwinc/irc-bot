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
with open('irc.json', 'r') as f:
    config = json.load(f)

server = config['server']
channel = config['channel']
botnick = config['botnick']
botpass = config['botpass']
adminname = config['adminname']
exitcode = config['exitcode'] + botnick

with open('cycle.json', 'r') as f:
    config = json.load(f)

cycle_high = config['cycle_high']
start_2020 = config['start_2020']

ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667
ircsock.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick +" "+ botnick +"\n", "UTF-8")) # user information
ircsock.send(bytes("NICK "+ botnick +"\n", "UTF-8")) # assign the nick to the bot

#API setup
#blockchair API
blockchair_base = 'https://api.blockchair.com/bitcoin/'
blockchair_headers = {'Content-Type': 'application/json'}

#blockchain API
blockchain_base = 'https://blockchain.info/'
blockchain_headers = {'Content-Type': 'application/json'}

#exchangeratesapi.io API
exchangerates_base = 'https://api.exchangeratesapi.io/'
exchangerates_headers = {'Content-Type': 'application/json'}

#gemini API
gemini_base = 'https://api.gemini.com/v1/'
gemini_headers = {'Content-Type': 'application/json'}

#irc functions
def joinchan(chan): # join channel(s).
  ircsock.send(bytes("JOIN "+ chan +"\n", "UTF-8")) 
  ircmsg = ""
  while ircmsg.find("End of /NAMES list.") == -1: 
    ircmsg = ircsock.recv(2048).decode("UTF-8")
    ircmsg = ircmsg.strip('\n\r')
    print(ircmsg)

def login():
  ircsock.send(bytes("PRIVMSG "+ "NickServ" +" :"+ "IDENTIFY "+ botpass +"\n", "UTF-8"))

def ping(): # respond to server Pings.
    ircsock.send(bytes("PONG :pingis\n", "UTF-8"))

def sendmsg(msg, target=channel): # sends messages to the target.
  ircsock.send(bytes("PRIVMSG "+ target +" :"+ msg +"\n", "UTF-8"))

def senderror(err=None):
    sendmsg("Something went wrong. See !help")
    if err is not None:
        print(f"[!] Command failed. {err}")
    else:
        print("[!] Command failed.")

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
            senderror()
    else:
        senderror()

def fx(cur1,cur2,amt):
    try:
        api_url = ('{0}latest?base=' + cur1).format(exchangerates_base)
        r = requests.get(api_url, headers=exchangerates_headers)
        if r.status_code == 200:
            d = json.loads(r.content.decode('UTF-8'))
            if d is not None:
                converted = float(d['rates'][cur2]) * float(amt)
                sendmsg("At a rate of " + '${:,.2f}'.format(d['rates'][cur2]) + " the converted amount is " +  '${:,.2f}'.format(converted))
            else:
               senderror() 
        else:
            senderror()
    except Exception as e:
        senderror(e)

def cycle():
    api_url = '{0}pubticker/btcusd'.format(gemini_base)
    r = requests.get(api_url, headers=gemini_headers)
    if r.status_code == 200:
        d = json.loads(r.content.decode('UTF-8'))
        if d is not None:
            try:
                delta = (float(d['last']) - float(cycle_high)) / float(cycle_high) * 100
                sendmsg("The change from the cycle high is " + str(delta) + "%")
            except Exception as e:
                senderror(e)
        else:
            senderror()
    else:
        senderror()

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
          sendmsg("!cycle                                               - Shows the difference in price from the last high", name)
          sendmsg("!fx <from_currency> <to_currency> <amount>           - Converts from one currency to another", name)
          sendmsg('!help                                                - Show this list', name)
          sendmsg('!tslb                                                - Print time of last block', name)
          sendmsg('!losers                                              - Print names of idiots to channel', name)
          sendmsg('!join                                                - attempt to channel', name)

        if message[:7].find('!join') != -1:
          joinchan(channel)

        if message[:7].find('!losers') != -1:
          sendmsg("Roger Ver, Craig Wright, Calvin Ayr")

        if message[:5].find('!tslb') != -1:
          tslb()

        if message[:3].find('!fx') != -1:
            try:
                from_cur = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1].split(' ',3)[1].upper()
                to_cur = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1].split(' ',3)[2].upper()
                amount = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1].split(' ',3)[3]
                fx(from_cur,to_cur,amount)
            except Exception as e:
                senderror(e)

        if message[:6].find('!cycle') != -1:
            cycle()

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
