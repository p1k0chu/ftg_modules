from .. import loader,utils

@loader.tds
class MsgCountMod(loader.Module):
    """Message counter"""

    strings = {
        "name": "MsgCount",
        "processing": "Извиняюсь...",
        "no_reply": "Нужно ответить на сообщение"
    }

    async def client_ready(self, client, db):
        self.client = client

    @loader.unrestricted
    @loader.ratelimit
    async def msgcountcmd(self, message):
        """.msgcount <reply> - count of message from user"""
        mmm = await utils.answer(
            message,
            self.strings("processing", message))
        
        reply = await message.get_reply_message()
        if not reply:
            return await utils.answer(
                mmm,
                self.strings("no_reply", message)
            )
        
        c = 0
        async for msg in message.client.iter_messages(
                entity=message.to_id):
            if msg.from_id == reply.from_id:
                c += 1
        
        return await utils.answer(
            mmm,
            f"Messages: {c}"
        )
