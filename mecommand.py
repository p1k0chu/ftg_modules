from .. import loader, utils

@loader.tds
class MeCommandMod(loader.Module):
    strings = {"name": "MeCommand",
               "output": "* <i><a href='tg://user?id={uid}'>{fullname}</a> {txt}</i>",
               "args_err": "Не корректные аргументы!",
               "user404": "Пользователь не найден :("}
    
    async def client_ready(self, client, db):
        self.client = client

    @loader.unrestricted
    @loader.ratelimit
    async def mecmd(self, message):
        """Использование: .me @<username> <text> or <id> <text>"""
        args = utils.get_args(message)
        #await utils.answer(message, str(args))
        if len(args) < 2:
            await utils.answer(message, self.strings("args_err", message))
            return
        try:
            user = int(args[0])
        except ValueError:
            user = args[0]
        try:
            user = await self.client.get_entity(user)
        except ValueError as e:
            await utils.answer(message, self.strings("user404", message))
            return
        
        fullname = user.first_name
        if user.last_name:
            fullname += " " + user.last_name
        await utils.answer(message, self.strings("output", message).format(uid=user.id, txt=" ".join(args[1:]), fullname=fullname))
