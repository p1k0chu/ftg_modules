from .. import loader, utils
import telethon
import os
import instaloader
import re
import urllib

@loader.tds
class InstaLoaderMod(loader.Module):
    """Downloads posts from instagram using InstaLoader. Author is @p1k0chu"""
    
    #you can do localization for yourself if you want to
    strings = {"name": "InstaLoader",
                "args_err": "Something is wrong with arguments",
                "downloading": "<b>Downloading from Instagram...</b>",
                "loader_not_loading": "Something is broken. Pls contact author and send him link to the Instagram post caused this problem (or fix it yourself xd)",
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
        """.instas <shortcode> - silent version"""
        await self.instacmd(message, silent = True)
    
    @loader.unrestricted
    @loader.ratelimit
    async def instacmd(self, message, silent = False):
        """.insta <shortcode> - download post by shortcode"""
        
        if silent:
            await message.delete()
        
        args = utils.get_args(message)
        
        #there should be only one argument
        if len(args) != 1:
            if not silent:
                await utils.answer(message, self.strings("args_err", message))
            return
        
        #TODO url parsing
        
        #let user know you handle command
        if not silent:
            await utils.answer(message, self.strings("processing", message))
        
        post = instaloader.Post.from_shortcode(self.il.context, args[0])
        
        #let user know you downloading files
        if not silent:
            await utils.answer(message, self.strings("downloading", message))
        #clean cache folder in case something left
        await clean_files()
        
        #download files to cache folder
        self.il.download_post(post, "instaloader_cache")
        #make list of all media files matching my_filer(file_name)
        resources = list(filter(my_filter, ["instaloader_cache/"+i for i in os.listdir("instaloader_cache")]))
            
        if len(resources) >= 1:
            #let user know you downloaded everithing and now uploading
            #do this instead of deleting message bc user would think it doesn't work 
            if not silent:
                await utils.answer(message, self.strings("uploading", message))
            #upload files
            if message.reply_to == None:
                await self.client.send_file(message.to_id, resources)
            else:
                await self.client.send_file(message.to_id, resources, reply_to=message.reply_to.reply_to_msg_id)
            #delete original message
            if not silent: # if silent = True message deleted already
                await message.delete()
        else:
            #idk why but cache folder has no media files
            #report if this happens
            if not silent:
                await utils.answer(message, self.strings("loader_not_loading", message))
        
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