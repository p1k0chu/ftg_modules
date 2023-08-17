from .. import loader,utils

@loader.tds
class TestMod(loader.Module):
    """Test module"""
    strings = {
        "name": "Test"
    }

    async def client_ready(self, client, db):
        self.client = client
    
    @loader.unrestricted
    @loader.ratelimit
    async def printmessagecmd(self, message):
        return await utils.answer(
            message,
            str(message.__dict__)
        )
        