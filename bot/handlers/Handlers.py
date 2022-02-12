import io
from uuid import uuid4
from telegram import Update, Bot, InlineQueryResultArticle, InputTextMessageContent
from reportlab.lib import colors
from telegram.parsemode import ParseMode
from reportlab.lib.pagesizes import inch
from bot.api.WeatherAPI import WeatherAPI
from bot.database.DBUtils import DBUtils
from bot.interactions.Keyboards import Keyboard
from bot.configuration.Configuration import Configuration
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from bot.api.ClasseVivaAPI import ClasseVivaAgendaAPI
from bot.interactions.GoodMorning import GoodMorning
from telegram.error import BadRequest


class Handlers:
    def __init__(self, cvv_uname: str, cvv_passwd: str, accu_weather_token: str, bot: Bot):
        self.enable_cvv = bool(cvv_uname and cvv_passwd)
        self.cvv = None
        if self.enable_cvv:
            self.cvv = ClasseVivaAgendaAPI()
            if not self.cvv.login(cvv_uname, cvv_passwd):
                self.enable_cvv = False
        else:
            print("Agenda Classeviva non abilitata")
        self.db_utils = DBUtils()
        self.c = Configuration(self.db_utils, self.enable_cvv)
        self.w = WeatherAPI(accu_weather_token, self.c.city_code)
        self.c.attach_weather(self.w)
        self.k = Keyboard(self.c)
        self.b = bot
        GoodMorning(self.b, self.c, self.k).start()

    def _generate_photo(self) -> io.BytesIO:
        i = io.BytesIO()
        elements = []
        schedules = self.c.subjects_schedule
        values = list(schedules.values())
        h = 0
        for x in values:
            if len(x) > h:
                h = len(x)
        h += 1
        w = len(schedules) + 1

        pagesize = (round(w * 1.8 * inch, 2) + 100, round(h * 0.4 * inch, 2) + 160)
        doc = SimpleDocTemplate(
            i,
            pagesize=pagesize
        )

        data = [["" for _ in range(w)] for _ in range(h)]
        keys = [self.c.days_translation[x] for x in schedules.keys()]
        keys.insert(0, " ")
        data[0] = keys

        for x in range(len(values)):
            for o, s in enumerate(values[x], start=1):
                data[o][0] = str(o)
                data[o][x + 1] = s.split("(", 1)[0]

        t = Table(data, [0.4 * inch] + (w - 1) * [2 * inch], h * [0.4 * inch])

        t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BACKGROUND', (0, 0), (-1, -0), colors.aquamarine),
            ('BACKGROUND', (0, 1), (0, -1), colors.aquamarine)
        ]))

        elements.append(t)
        # write the document to disk
        doc.build(elements)
        i.seek(0)
        return i

    def h_start(self, update: Update, _):
        payload = update.message.text.split(" ")
        chat_id = update.message.chat.id
        if self.db_utils.is_user(chat_id):
            if self.db_utils.is_stopped(chat_id):
                self.db_utils.start(chat_id)
            update.message.reply_text(
                self.c.get_formatted_message(self.c.start_message, chat_id),
                parse_mode=ParseMode.HTML,
                reply_markup=self.k.create_keyboard_main(self.enable_cvv),
                disable_web_page_preview=True
            )
        elif len(payload) > 1 and self.db_utils.is_valid_token(payload[1]):
            print(update.message.chat)
            self.db_utils.add_user(update.message.chat.id, update.message.chat.first_name, update.message.chat.username)
            update.message.reply_text(
                self.c.get_formatted_message(self.c.start_message, chat_id),
                parse_mode=ParseMode.HTML,
                reply_markup=self.k.create_keyboard_main(self.enable_cvv),
                disable_web_page_preview=True
            )
        else:
            update.message.reply_text("Non sei autorizzato ad usare questo bot")

    def h_settings(self, update: Update, _):
        chat_id = update.message.chat.id
        if not self.db_utils.is_user(chat_id):
            return
        update.message.reply_text(
            "Seleziona le impostazioni da modificare:",
            reply_markup=self.k.create_keyboard_settings(self.db_utils.is_admin(chat_id))
        )

    def h_info(self, update: Update, _):
        update.message.reply_text(
            self.c.info,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )

    def h_announcement(self, update: Update, _):
        chat_id = update.message.chat.id
        if not self.db_utils.is_admin(chat_id):
            return

        text = update.message.text.split(" ", 1)
        if len(text) != 2:
            update.message.reply_text(
                "Sintassi non valida. La sintassi corretta del comando è:\n<code>/annuncio {testo}</code>",
                parse_mode=ParseMode.HTML
            )
            return
        update.message.reply_text(
            text[1],
            parse_mode=ParseMode.HTML,
            reply_markup=self.k.ask_for_confirmation()
        )
        self.db_utils.update_broadcast_message(chat_id, text[1])

    def h_stop(self, update: Update, _):
        chat_id = update.message.chat.id
        if not self.db_utils.is_user(chat_id):
            return
        self.db_utils.stop(chat_id)
        update.message.reply_text(
            "Bot stoppato. ✅\n"
            "Non riceverai più il buongiorno o eventuali comunicazioni.\n"
            "Per riavviarmi digita /start"
        )

    def h_reload(self, update: Update, _):
        chat_id = update.message.chat.id
        if not self.db_utils.is_admin(chat_id):
            return

        self.c.load_config()
        update.message.reply_text("Configurazione ricaricata ✅", reply_markup=self.k.create_keyboard_home())

    def _handle_image(self, update: Update):
        update.callback_query.bot.send_document(update.callback_query.message.chat.id, self._generate_photo(),
                                                filename="orario.pdf")

    def _handle_day_choice(self, update: Update, data: list):
        schedule = self.c.get_parsed_subjects_schedule(data[1])
        update.callback_query.edit_message_text(
            (f"Ecco l'orario di {self.c.days_translation[data[1]]}:\n<b>" if schedule else "") +
            schedule + "</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=self.k.create_keyboard_home()
        )

    def _handle_home(self, update: Update, data: list):
        if len(data) > 1:
            update.callback_query.message.reply_text(
                self.c.get_formatted_message(self.c.start_message, update.callback_query.message.chat.id),
                parse_mode=ParseMode.HTML,
                reply_markup=self.k.create_keyboard_main(self.enable_cvv),
                disable_web_page_preview=True
            )
            return
        update.callback_query.edit_message_text(
            self.c.get_formatted_message(self.c.start_message, update.callback_query.message.chat.id),
            parse_mode=ParseMode.HTML,
            reply_markup=self.k.create_keyboard_main(self.enable_cvv),
            disable_web_page_preview=True
        )

    def _handle_filter(self, update: Update, page: int = 0):
        update.callback_query.edit_message_text(
            "Seleziona la materia:",
            reply_markup=self.k.create_keyboard_filter(page)
        )

    def _handle_filter_subject(self, update: Update, subject: str, page: int = 0):
        if subject not in self.c.all_subjects:
            return

        m = []

        for day, subjects in self.c.subjects_schedule.items():
            for sub in enumerate(subjects, start=1):
                if sub[1].split("(", 1)[0].strip() == subject:
                    m.append(f"{self.c.days_translation[day]} a {sub[0]}^ ora")

        update.callback_query.edit_message_text(
            f"Ecco quando abbiamo {subject}:\n<b>" + "\n".join(m) + "</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=self.k.create_keyboard_back(page)
        )

    def _handle_agenda(self, update: Update):
        if not self.enable_cvv:
            update.callback_query.answer("Function not enabled")
            return

        update.callback_query.answer("Sto leggendo l'agenda...")
        agenda = self.cvv.agenda()
        update.callback_query.edit_message_text(
            agenda,
            parse_mode=ParseMode.HTML,
            reply_markup=self.k.create_keyboard_home()
        )

    def _handle_send_announcement(self, update: Update):
        chat_id = update.callback_query.message.chat.id
        if not self.db_utils.is_admin(chat_id) or self.db_utils.get_broadcast_message(chat_id).replace("None",
                                                                                                       "") == "":
            update.callback_query.answer()
            return

        for user in self.db_utils.list_users_chat_id(stopped=False):
            if chat_id == user:
                continue
            self.b.send_message(
                user,
                self.db_utils.get_broadcast_message(chat_id),
                reply_markup=self.k.create_keyboard_home(new_message=True),
                parse_mode=ParseMode.HTML
            )

        self.db_utils.update_broadcast_message(chat_id, "None")
        update.callback_query.message.edit_reply_markup(reply_markup=self.k.create_keyboard_home())

    def _handle_cancel(self, update: Update):
        chat_id = update.callback_query.message.chat.id
        if not self.db_utils.is_admin(chat_id) or self.db_utils.get_broadcast_message(chat_id).replace("None",
                                                                                                       "") == "":
            update.callback_query.answer()
            return

        self.db_utils.update_broadcast_message(chat_id, "None")
        update.callback_query.message.edit_reply_markup(reply_markup=self.k.create_keyboard_home())
        update.callback_query.answer("Operazione annullata.")

    def _handle_gm(self, update: Update, is_global: bool = False):
        chat_id = update.callback_query.message.chat.id
        if is_global:
            if not self.db_utils.is_admin(chat_id):
                return
            try:
                update.callback_query.edit_message_text(
                    "Vuoi abilitare o disabilitare il buongiorno globale?\n"
                    f"Lo stato corrente è <b>{'✅ Abilitato' if self.c.enable_gm else '❌ Disabilitato'}</b>",
                    parse_mode=ParseMode.HTML,
                    reply_markup=self.k.create_keyboard_enable_disable(is_global=True)
                )
            except BadRequest:
                pass
            update.callback_query.answer()
            return

        try:
            update.callback_query.edit_message_text(
                "Vuoi abilitare o disabilitare il buongiorno?\n"
                f"Lo stato corrente è <b>{'✅ Abilitato' if self.c.enable_gm else '❌ Disabilitato'}</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=self.k.create_keyboard_enable_disable(is_global=False)
            )
        except BadRequest:
            pass
        update.callback_query.answer()

    def _set_gm(self, update: Update, is_global, status: bool):
        chat_id = update.callback_query.message.chat.id
        if is_global:
            if not self.db_utils.is_admin(chat_id):
                return
            self.c.enable_gm = status
            update.callback_query.answer("Fatto")
            try:
                update.callback_query.edit_message_text(
                    "Vuoi abilitare o disabilitare il buongiorno globale?\n"
                    f"Lo stato corrente è <b>{'✅ Abilitato' if self.c.enable_gm else '❌ Disabilitato'}</b>",
                    parse_mode=ParseMode.HTML,
                    reply_markup=self.k.create_keyboard_enable_disable(is_global=True)
                )
            except BadRequest:
                pass
            return

        self.db_utils.set_gm(chat_id, status)
        update.callback_query.answer("Fatto")
        try:
            update.callback_query.edit_message_text(
                "Vuoi abilitare o disabilitare il buongiorno?\n"
                f"Lo stato corrente è <b>{'✅ Abilitato' if self.db_utils.gm_status(chat_id) else '❌ Disabilitato'}</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=self.k.create_keyboard_enable_disable()
            )
        except BadRequest:
            pass
        return

    def h_callback_query(self, update: Update, _):
        chat_id = update.callback_query.message.chat.id

        if not self.db_utils.is_user(chat_id):
            update.callback_query.answer()
            return

        data = update.callback_query.data
        data = data.split("#", 1)

        if data[0] == "DAY":
            self._handle_day_choice(update, data)
            update.callback_query.answer()
            return

        if data[0] == "HOME":
            self._handle_home(update, data)
            update.callback_query.answer()
            return

        if data[0] == "FILTER":
            if len(data) > 1 and data[1].isdecimal():
                self._handle_filter(update, int(data[1]))
            else:
                self._handle_filter(update)
            update.callback_query.answer()
            return

        if data[0] == "SUB":
            if len(data) == 1:
                update.callback_query.answer()
                return

            data = data[1].split("#")
            if len(data) > 1:
                self._handle_filter_subject(update, data[0], int(data[1]))

            update.callback_query.answer()
            return

        if data[0] == "PHOTO":
            update.callback_query.answer("File in arrivo")
            self._handle_image(update)
            return

        if data[0] == "AGENDA":
            self._handle_agenda(update)
            return

        if data[0] == "SEND":
            self._handle_send_announcement(update)
            return
        if data[0] == "CANCEL":
            self._handle_cancel(update)
            return

        if data[0] == "GM":
            self._handle_gm(update, is_global=(len(data) == 2 and data[1] == "GLOBAL"))
            return

        if data[0] == "ENABLE":
            self._set_gm(update, (len(data) == 2 and data[1] == "GLOBAL"), True)
            return

        if data[0] == "DISABLE":
            self._set_gm(update, (len(data) == 2 and data[1] == "GLOBAL"), False)
            return

        print(data)

    def h_inline_query(self, update: Update, _):
        if not self.db_utils.is_user(update.inline_query.from_user.id):
            update.inline_query.answer([
                InlineQueryResultArticle(
                    id=uuid4(),
                    title="Ehi, chi sei tu per usarmi?",
                    input_message_content=InputTextMessageContent(
                        "Ehi, chi sei tu per usarmi? <a hred=\"https://i.imgur.com/gLlmEeb.jpg\">🤔</a>",
                        parse_mode=ParseMode.HTML,
                    )
                )
            ], cache_time=20)
            return
        days = self.c.working_days
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title=self.c.days_translation[x],
                input_message_content=InputTextMessageContent(
                    f"Ecco l'orario di {self.c.days_translation[x]}:\n<b>{self.c.get_parsed_subjects_schedule(x)}</b>",
                    parse_mode=ParseMode.HTML
                ),
            ) for x in days
        ]

        update.inline_query.answer(results, cache_time=20)
