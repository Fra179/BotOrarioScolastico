from telegram.ext import Updater, CommandHandler, Dispatcher, CallbackQueryHandler, InlineQueryHandler
from bot.handlers.Handlers import Handlers


class Bot:
    def __init__(self, token: str, cvv_uname: str, cvv_passwd: str, accu_weather_token: str):
        self.u = Updater(token, use_context=True)

        d: Dispatcher = self.u.dispatcher

        h = Handlers(cvv_uname, cvv_passwd, accu_weather_token, d.bot)

        command_handlers = [
            ("start", h.h_start),
            ("settings", h.h_settings),
            ("help", h.h_info),
            ("annuncio", h.h_announcement),
            ("stop", h.h_stop),
            ("reload", h.h_reload)
        ]

        for command, handler in command_handlers:
            d.add_handler(CommandHandler(command, handler))

        d.add_handler(CallbackQueryHandler(h.h_callback_query))
        d.add_handler(InlineQueryHandler(h.h_inline_query))

    def start(self):
        self.u.start_polling()
        self.u.idle()
