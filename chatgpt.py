# i made this module for myself 
# but i don't have paid plan in openai
# and i didn't test if this module works
# but i'll leave it on github

import openai
from .. import loader, utils
import telethon
import os

@loader.tds
class ChatGptMod(loader.Module):
    """Use ChatGPT for whatever you want"""
    
    strings = {
        "name": "ChatGPT",
        "api_key_cfg_doc": "Your API key for OpenAI",
        "api_key_missing": "API key is missing",
        "api_key_invalid": "API key is invalid",
        "no_args": "Enter prompt or reply to a message",
        "ratelimiterror": "You exceeded your current quota and can't use ChatGPT api"
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig("api_key", "", lambda: self.strings["api_key_cfg_doc"])
    
    async def client_ready(self, client, db):
        self.client = client
    
    @loader.unrestricted
    @loader.ratelimit
    async def gptcmd(self, message):
        """.gpt <text> or <reply> - generate with ChatGPT"""
        
        #check for api key existance
        if self.config["api_key"] == "":
            await utils.answer(message, self.strings("api_key_missing", message))
        
        openai.api_key = self.config["api_key"]
        text = utils.get_args_raw(message)
        if not text:
            if message.is_reply:
                text = (await message.get_reply_message()).message
            else:
                await utils.answer(message, self.strings("no_args", message))
                return
        
        try:
            r = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo", messages=[{"role": "system", "content": "You are a helpful assistant."}, 
                                                                          {"role": "user", "content": text}],
                                             n=1) #if doesn't work delete 'n' argument
        except openai.error.AuthenticationError:
            await utils.answer(message.self.strings("api_key_invalid", message))
            return
        except openai.error.RateLimitError:
            await utils.answer(message, self.strings("ratelimiterror", message))
            return
        
        await utils.answer(message, r.choices[0].message.content)