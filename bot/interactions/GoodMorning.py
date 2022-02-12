import time
from telegram import Bot
from threading import Thread
from datetime import datetime
from telegram.parsemode import ParseMode
from bot.interactions.Keyboards import Keyboard
from bot.configuration.Configuration import Configuration
from bot.database.DBStructure import db_session, User, select, commit


class GoodMorning(Thread):
    def __init__(self, bot: Bot, config: Configuration, keyboard: Keyboard):
        self.bot = bot
        self.c = config
        self.k = keyboard
        super().__init__()

    def run(self):
        while 1:
            if not self.c.enable_gm:
                print("Not Enabled")
                time.sleep(300)
                continue
            now = datetime.now()
            print("Checking")
            print(now.hour, now.minute, self.c.notification_time.hour, self.c.notification_time.minute)
            if now.hour == self.c.notification_time.hour and \
                    now.minute == self.c.notification_time.minute:
                print("Done")
                with db_session:
                    for user in select(x for x in User if not x.stopped and not x.stop_gm):
                        # if user.was_notified:
                        #    continue
                        if self.c.audio_file is not None:
                            self.bot.send_voice(chat_id=user.chat_id, voice=open(self.c.audio_file, 'rb'))
                        if datetime.now().strftime('%a').lower() in self.c.working_days:
                            message = self.c.get_formatted_message(self.c.school_day_message, user.chat_id)
                            disable_web_page_preview = True
                        else:
                            message = self.c.get_formatted_message(self.c.free_day_message, user.chat_id)
                            disable_web_page_preview = False
                        self.bot.send_message(
                            user.chat_id,
                            message,
                            parse_mode=ParseMode.HTML,
                            reply_markup=self.k.create_keyboard_home(),
                            disable_web_page_preview=disable_web_page_preview
                        )
                        # user.was_notified = True
                        commit()
                    print("sleeping 30")
                    time.sleep(30)
                print("sleeping 30")
            time.sleep(30)
