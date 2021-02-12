#!/usr/bin/python3
# Bot framework by Linux Academy at https://github.com/Orderchaos/LinuxAcademy-IRC-Bot

import socket
import requests
import json
import datetime
import time
from datetime import timedelta
from datetime import datetime

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

ath = float(config['cycle_high'])
new_high = 0

reset = "\x03"
blue = "\x0302"
green = "\x0303"
red = "\x034"
yellow = "\x038"
white = "\x0300"

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

#cme futures fake API
cme_base = 'https://www.cmegroup.com/CmeWS/mvc/Quotes/Future'
cme_headers = {'Content-Type': 'application/json'}

gemini_base = 'https://api.gemini.com/v1/'
gemini_base2 = 'https://api.gemini.com/v2/'
coincap_base = 'https://api.coincap.io/v2/assets/'

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

def rank(c):
  try:
    tickers = requests.get(f'{coincap_base}?limit=500')
    tickers.raise_for_status()

    asset = next(i["id"] for i in tickers.json()["data"] if i["symbol"] == c.upper())

    coin = requests.get(f'{coincap_base}{asset}')    
    coin.raise_for_status()

    ch_color = reset if float(coin.json()["data"]["changePercent24Hr"]) < 0 else green
    sendmsg(f'{coin.json()["data"]["name"]} [CoinCap] -> ${float(coin.json()["data"]["priceUsd"]):,.2f} ({ch_color}{float(coin.json()["data"]["changePercent24Hr"]):,.2f}%{reset}) | volume: ${float(coin.json()["data"]["volumeUsd24Hr"]):,.2f} | rank: {coin.json()["data"]["rank"]}')

  except Exception as e:
    senderror(str(e))

def satoshi(sats):
    try:
        ticker = requests.get(f'{gemini_base}pubticker/btcusd')
        ticker.raise_for_status()

        value = (float(ticker.json()["last"])) * (sats / 10000000)
        sendmsg(f'At a BTC price of ${float(ticker.json()["last"]):,.2f}, $sats satoshi is ${value:,.2f}')

    except Exception as e:
    senderror(str(e))

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
    try:
        global new_high
        global ath
        ticker = requests.get(f'{gemini_base}pubticker/btcusd')
        ticker.raise_for_status()
  
        pricefeed = requests.get(f'{gemini_base}pricefeed')
        pricefeed.raise_for_status()

        high = requests.get(f'{gemini_base2}/ticker/btcusd')
        high.raise_for_status()

        future = requests.get(f'{cme_base}/8478/G')
        future.raise_for_status()

        future_price = float(next(i["last"] for i in future.json()["quotes"] if i["isFrontMonth"]))

        this_high = (float(high.json()['high']))

        if this_high > ath:
          new_high = this_high

        if new_high > ath:
          ath = new_high

        stop = (float(ath)) * 0.9

        percent_of_ath = ( float(ticker.json()["last"]) / ath - 1 ) * 100
        percentChange24h = float(next(i["percentChange24h"] for i in pricefeed.json() if i["pair"] == "BTCUSD")) * 100
        
        pc24_color = reset if percentChange24h < 0 else green
        pcath_color = reset if percent_of_ath < 0 else green

        sendmsg(f'BTC [Gemini/CME] -> ${float(ticker.json()["last"]):,.2f} ({pc24_color}{percentChange24h:,.2f}%{reset} 24H) (F: {blue}${future_price:,.2f}{reset}) | All-Time High: ${ath:,.2f} ({pcath_color}{percent_of_ath:,.2f}%{reset}) | ATH Stop: ${float(stop):,.2f} (-10%)') 

    except Exception as e:
        senderror(str(e))

def vol():
    try:
        coincap = requests.get(f'{coincap_base}bitcoin')
        coincap.raise_for_status()
        
        vol_in_bill = float(coincap.json()['data']['volumeUsd24Hr']) / 1000000000
        sendmsg(f'BTC [Coincap] -> 24H Volume: ${vol_in_bill:,.2f} billion USD')

    except Exception as e:
        senderror(str(e))


def main():
  login()

  FIFTEEN_MINS = timedelta(seconds=60*15)
  last_run = datetime.now() - FIFTEEN_MINS
  
  while 1:
    ircmsg = ircsock.recv(2048).decode("UTF-8")
    ircmsg = ircmsg.strip('\n\r')
    print(ircmsg)

    if datetime.now() - last_run > FIFTEEN_MINS:
      last_run = datetime.now()
      #cycle() - removed until I can make it less chatty

    if ircmsg.find("PRIVMSG") != -1:
      name = ircmsg.split('!',1)[0][1:]
      message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]
      if len(name) < 17:
        
       ##################################################################
       # Commands go here

        if message[:5].find('!help') != -1:
          sendmsg(f'Command List:', name)
          sendmsg(f'!c                                                   - Show change from last high, daily change', name)
          sendmsg(f'!r <ticker>                                          - Show coin stats from Coincap. BTC is default.', name)
          sendmsg(f'!fx <from_currency> <to_currency> <amount>           - Converts from one currency to another', name)
          sendmsg(f'!help                                                - Show this list', name)
          sendmsg(f'!tslb                                                - Print time of last block', name)
          sendmsg(f'!losers                                              - Print names of idiots to channel', name)
          sendmsg(f'!join                                                - attempt to channel', name)
          sendmsg(f'!vol                                                 - Show 24 hour BTC volume', name)

        if message[:2].find('!r') != -1:
          try:
            coin = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1].split(' ',1)[1]
            if not coin:
              coin = "BTC"
            rank(coin)
          except Exception as e:
            senderror(e)

        if message[:4].find('!vol') != -1:
          vol()

        if message[:7].find('!join') != -1:
          joinchan(channel)

        if message[:7].find('!losers') != -1:
          sendmsg("Roger Ver, Craig Wright, Calvin Ayr")

        if message[:3].find('!fx') != -1:
            try:
                from_cur = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1].split(' ',3)[1].upper()
                to_cur = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1].split(' ',3)[2].upper()
                amount = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1].split(' ',3)[3]
                fx(from_cur,to_cur,amount)
            except Exception as e:
                senderror(e)

        if message[:2].find('!c') != -1:
            cycle()

        if message[:3].find('!s ') != -1:
            satoshi()

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
