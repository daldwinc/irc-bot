# IRC-Bot

Framework based on: https://linuxacademy.com/blog/geek/creating-an-irc-bot-with-python3/

Before you begin

1. Install prerequisites

```	
apt install python-pip
pip install requests
```

2. Create config file in bot directory.

```
touch irc.json
echo '{' > irc.json
echo '        "server": "test3.server.com",' >> irc.json
echo '        "channel": "#testchannel",' >> irc.json
echo '        "botnick": "yourbotsnick",' >> irc.json
echo '        "adminname": "yourircnick",' >> irc.json
echo '        "exitcode": "word"' >> irc.json
echo '}' >> irc.json
```
3. Run bot

```
python3 bot.py
```
