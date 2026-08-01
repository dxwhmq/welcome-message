# welcome-message
пишет заранее подготовленный текст всем новым участникам чата.
from .. import loader, utils


@loader.tds
class WelcomeMod(loader.Module):
    """Приветствует новых участников чата заранее подготовленным сообщением"""

    strings = {
        "name": "Welcome",
        "cfg_text": "текст приветствия. Используй {name} - туда подставится имя нового участника.",
        "set_success": "текст приветствия обновлён!",
        "current_text":  текущий текст приветствия:\n\n{text}",
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

    @loader.watcher(chat_action=True)
    async def watcher(self, message):
        if not (getattr(message, "user_joined", False) or getattr(message, "user_added", False)):
            return

        user = await message.get_user()
        name = utils.escape_html(user.first_name or "друг")

        text = self.config["welcome_text"].format(name=name)

        await message.reply(text)

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
