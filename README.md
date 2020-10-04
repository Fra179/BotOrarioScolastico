## Bot Orario Scolastico
# Introduction
This bot will help you keep track of your school schedule by reminding you every morning of your daily subjects.
The bot also features an integration with [Classeviva](https://web.spaggiari.eu/home/app/default/login.php)'s Agenda section (a shitty online school register) so it can also list you all the written and oral tests your teachers have planned in the next 14 days.

# Cloning the bot
First things first, you need to clone the repo (yeah, pretty basic stuff here, I really don't know why I wrote this section) and then cd into that directory.
In case you don't know how to do that:
```bash
git clone https://github.com/Fra179/BotOrarioScolastico.git
cd BotOrarioScolastico
```

# Configuration
Good job! You are very good at cloning repos, now you need to configure the bot.
I already wrote an example configuration. It's named ```configuration-example.json```. If you are ok with the dafault values, you can just rename it by typing
```bash
mv configuration-example.json configuration.json
```
Otherwise, just edit the configuration with your editor of choice and then issue the command above.

# Running
Well done, now you need to install all the dependencies. Just type the command:
```bash
python3 -m pip install -r requirements.txt
```

And now there is the hard part, are you ready?  
_Just kidding_, there is nothing hard in starting this bot.
It only needs a few environment variables to run properly:
```
TOKEN={telegram-bot-token}
CVV_UNAME={ClasseViva username}
CVV_PASSWD={ClasseViva password}
ACCU_WEATHER_TOKEN={accuWeather API token}
```
The last three vars aren't mandatory, the bot will notice if they are missing and it will automatically disable the related features (at least this is what it's supposed to do).

Finally, you can run the bot with
```bash
python3 bot.py
```

Good job, we are done! It was easy, wasn't it?
