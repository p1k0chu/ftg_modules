from .. import loader, utils
import telethon
import os
import instaloader
import re

re_comp = re.compile(r"https?://www.instagram.com/(?:p|reel)/(\S+)/")

@loader.tds
class InstaLoaderMod(loader.Module):
    """Downloads posts from instagram using InstaLoader. Author is t.me/p1k0chu"""
    
    #you can do localization for yourself if you want to
    strings = {"name": "InstaLoader",
                "args_err": "There is no URL",
                "processing": "<b>Processing...</b>",
                "uploading": "<b>Uploading files...</b>"}
    
    def __init__(self):
        self.il = instaloader.Instaloader(download_video_thumbnails = False,
                                          save_metadata = False,
                                          quiet = True)
    
    async def client_ready(self, client, db):
        self.client = client
    
    @loader.unrestricted
    @loader.ratelimit
    async def instascmd(self, message):
        """.instas <url> - silent version"""
        await self.instacmd(message, silent = True)
    
    @loader.unrestricted
    @loader.ratelimit
    async def instacmd(self, message, silent = False):
        """.insta <url> - download post by url"""
        
        if silent:
            await message.delete()
        
        text = utils.get_args_raw(message)
        
        #there should be only one argument
        if not text and message.is_reply:
            text = (await message.get_reply_message()).message
        
        if not text:
            await utils.answer(message, self.strings("args_err", message))
            return
        
        codes = re.findall(re_comp, text)
        if not codes:
            await utils.answer(message, self.strings("args_err", message))
            return
        
        #let the user know you handling command
        if not silent:
            await utils.answer(message, self.strings("processing", message))
        
        for i in codes:
            post = instaloader.Post.from_shortcode(self.il.context, i)
            #download files to cache folder
            self.il.download_post(post, "instaloader_cache")
        
        resources = list(filter(my_filter, ["instaloader_cache/"+i for i in os.listdir("instaloader_cache")]))
        
        if len(resources) >= 1:
            #let user know you downloaded everithing and now uploading
            #do this instead of deleting message bc user would think it doesn't work 
            if not silent:
                await utils.answer(message, self.strings("uploading", message))
            #upload files
            if message.reply_to:
                await self.client.send_file(message.to_id if message.out else message.from_id, resources, reply_to=message.reply_to.reply_to_msg_id)
            else:
                await self.client.send_file(message.to_id if message.out else message.from_id, resources)
            #delete original message
            if not silent: # if silent = True message deleted already
                await message.delete()
        
        #clean after yourself
        await clean_files()

async def clean_files():
    #linux
    if os.name == "posix":
        return os.system("rm -rf instaloader_cache/*")
    #windows
    elif os.name == "nt":
        return os.system(r"del /Q .\instaloader_cache\*")

def my_filter(x):
    return not (x.endswith(".txt") or x.endswith(".xz") or x.endswith(".json"))