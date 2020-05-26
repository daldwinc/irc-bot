# LinuxAcademy-IRC-Bot
 Code for the bot created here: https://linuxacademy.com/blog/geek/creating-an-irc-bot-with-python3/
 Feel free to share/edit/whatever! Just please credit Linux Academy as the source if copying!

Before you begin:
```	
apt install python-pip
pip install requests
```

Create config file in bot directory:

*replace parameters with real values

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
