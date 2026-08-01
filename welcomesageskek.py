from herokutl import events
from .. import loader, utils


@loader.tds
class WelcomeMod(loader.Module):
    """приветствует новых участников чата заранее подготовленным сообщением"""

    strings = {
        "name": "Welcome",
        "cfg_text": "текст приветствия. используй {name} - туда подставится имя нового участника.",
        "set_success": "текст приветствия обновлён!",
        "current_text": "текущий текст приветствия:\n\n{text}",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "welcome_text",
                "привет, {name}! добро пожаловать в чат",
                lambda: self.strings("cfg_text"),
            ),
        )

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        client.add_event_handler(self._on_chat_action, events.ChatAction())

    def _enabled_chats(self):
        return self.db.get("WelcomeMod", "enabled_chats", [])

    async def _on_chat_action(self, event):
        if not (getattr(event, "user_joined", False) or getattr(event, "user_added", False)):
            return

        if utils.get_chat_id(event) not in self._enabled_chats():
            return

        user = await event.get_user()
        name = utils.escape_html(user.first_name or "друг")

        text = self.config["welcome_text"].format(name=name)

        await self.client.send_message(
            event.chat_id,
            text,
            reply_to=event.id,
        )

    async def setwelcomecmd(self, message):
        args = utils.get_args_raw(message)

        if not args:
            await utils.answer(
                message,
                self.strings("current_text").format(text=self.config["welcome_text"]),
            )
            return

        self.config["welcome_text"] = args
        await utils.answer(message, self.strings("set_success"))

    async def welcomeoncmd(self, message):
        chats = self._enabled_chats()
        chat_id = utils.get_chat_id(message)

        if chat_id in chats:
            await utils.answer(message, "в этом чате приветствие уже включено")
            return

        chats.append(chat_id)
        self.db.set("WelcomeMod", "enabled_chats", chats)
        await utils.answer(message, "приветствие включено в этом чате")

    async def welcomeoffcmd(self, message):
        chats = self._enabled_chats()
        chat_id = utils.get_chat_id(message)

        if chat_id not in chats:
            await utils.answer(message, "в этом чате приветствие уже выключено")
            return

        chats.remove(chat_id)
        self.db.set("WelcomeMod", "enabled_chats", chats)
        await utils.answer(message, "приветствие выключено в этом чате")
