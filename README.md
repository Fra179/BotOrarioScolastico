## Bot Orario Scolastico
# Introduction
This bot will help you to get track of your school schedule by reminding you every morning of your daily subject schedule.
The bot also have integration with the Agenda of [Classeviva](https://web.spaggiari.eu/home/app/default/login.php?custcode=) (a shitty online school register) so it can also lists you all the written and oral tests that your teachers program within 14 days.

# Cloning the bot
First of all, you need to clone the repo (yeah, pretty basic stuff here, I really don't know why I wrote this section) and then cd into that dir.
In case you don't know how to do that:
```bash
git clone https://github.com/Fra179/BotOrarioScolastico.git
cd BotOrarioScolastico
```

# Configuration
Good job, you are so good at cloning repos, now you need to configure the bot.
I already wrote an example configuration. It's named ```configuration-example.json```. If you are ok with the dafault values, you can just rename it by typing
```bash
mv configuration-example.json configuration.json
```
Otherwise, just edit the configuration and then issue the command above.

# Running

Well done, now you need to install all the dependencies
```bash
python3 -m pip install -r requirements.txt
```

Now the hard part, are you ready?
Just kidding, there is nothing hard in starting this bot.
The bot need a few environment variables to run properly:
```
TOKEN={telegram-bot-token}
CVV_UNAME={classeviva username}
CVV_PASSWD={classeviva password}
ACCU_WEATHER_TOKEN={accu_weather_token}
```
The last three are option, the bot will be able of noticing if they are missing and will automatically disable the features that require them (or rather this is what it's supposed to do)

Finally, you can run the bot
```bash
python3 bot.py
```

And we are done. It was easy, wasn't it?