from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from bot.configuration.Configuration import Configuration


class Keyboard:
    def __init__(self, c: Configuration):
        self.c = c

    def create_keyboard_main(self, enable_cvv: bool = False) -> InlineKeyboardMarkup:
        days = self.c.working_days
        days = [days[i:i + 2] for i in range(0, len(days), 2)]
        keyboard = [
                       [
                           InlineKeyboardButton(text=self.c.days_translation[k], callback_data=f"DAY#{k}") for k in x
                       ] for x in days
                   ] + [
                       [
                           InlineKeyboardButton("🔍 Filtra per materie", callback_data="FILTER")
                       ]
                   ]
        if enable_cvv:
            keyboard.append([
                InlineKeyboardButton("🗓 Agenda", callback_data="AGENDA")
            ])
        keyboard.append([
            InlineKeyboardButton("📄 Foto Orario", callback_data="PHOTO")
        ])

        return InlineKeyboardMarkup(keyboard)

    def create_keyboard_home(self, new_message: bool = False) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text="🏠 Home", callback_data="HOME#NEW" if new_message else "HOME")
            ]
        ])

    def create_keyboard_filter(self, page: int = 0) -> InlineKeyboardMarkup:
        subjects = self.c.all_subjects
        subjects_pages = [subjects[i:i + 8] for i in range(0, len(subjects), 8)]
        subjects = [subjects_pages[page][i:i + 2] for i in range(0, len(subjects_pages[page]), 2)]

        if page > len(subjects):
            page = len(subjects) - 1

        keyboard = [
            [
                InlineKeyboardButton(text=m, callback_data=f"SUB#{m}#{page}") for m in x
            ] for x in subjects
        ]

        if page > 0:
            keyboard.append([
                InlineKeyboardButton(text="◀️ Indietro", callback_data=f"FILTER#{page - 1}")
            ])

        if page < len(subjects_pages) - 1:
            if page > 0:
                keyboard[-1].append(
                    InlineKeyboardButton(text="▶️ Avanti", callback_data=f"FILTER#{page + 1}")
                )
            else:
                keyboard.append([
                    InlineKeyboardButton(text="▶️ Avanti", callback_data=f"FILTER#{page + 1}")
                ])

        keyboard.append([
            InlineKeyboardButton(text="🏠 Home", callback_data="HOME")
        ])

        return InlineKeyboardMarkup(keyboard)

    def create_keyboard_back(self, page: int = 0) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text="◀️ Indietro", callback_data=f"FILTER#{page}")
            ]
        ])

    def ask_for_confirmation(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text="📩 Invia", callback_data="SEND"),
                InlineKeyboardButton(text="❌ Annulla", callback_data="CANCEL")
            ]
        ])

    def create_keyboard_settings(self, is_admin: bool = False) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [

                InlineKeyboardButton(text="💬 Buongiorno", callback_data="GM"),
            ],
            [
                InlineKeyboardButton(text="💬 Buongiorno Globale", callback_data="GM#GLOBAL"),
            ],
            [
                InlineKeyboardButton(text="🏠 Home", callback_data="HOME")
            ]
        ]) if is_admin else InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text="💬 Buongiorno", callback_data="GM"),
            ],
            [
                InlineKeyboardButton(text="🏠 Home", callback_data="HOME")
            ]
        ])

    def create_keyboard_enable_disable(self, is_global: bool = False) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text="✅ Abilita", callback_data=f"ENABLE{'#GLOBAL' if is_global else ''}"),
                InlineKeyboardButton(text="❌ Disabilita", callback_data=f"DISABLE{'#GLOBAL' if is_global else ''}"),

            ],
            [
                InlineKeyboardButton(text="🏠 Home", callback_data="HOME")
            ]
        ])
