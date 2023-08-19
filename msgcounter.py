from .. import loader,utils

@loader.tds
class MsgCountMod(loader.Module):
    """Message counter"""

    strings = {
        "name": "MsgCount",
        "processing": "Рахую повідомлення...",
        "no_reply": "Потрібно відповісти на повідомлення",
        "output": "Кількість повідомлень: {}"
    }

    async def client_ready(self, client, db):
        self.client = client

    @loader.unrestricted
    @loader.ratelimit
    async def msgcountcmd(self, message):
        """.msgcount <reply> - count messages from user"""
        await utils.answer(message, self.strings("processing", message))
        
        reply = await message.get_reply_message()
        if not reply:
            await utils.answer(message, self.strings("no_reply", message))
        
        c = len(await message.client.get_messages(entity=message.to_id, from_user=reply.from_id))
        
        await utils.answer(message, self.strings("output", message).format(c))
