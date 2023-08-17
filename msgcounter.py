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
        
        c = 0
        async for msg in message.client.iter_messages(
                entity=message.to_id):
            if msg.from_id == reply.from_id:
                c += 1
        
        await utils.answer(message, self.strings("output", message).format(c))
