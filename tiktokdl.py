from tiktokapipy.async_api import AsyncTikTokAPI
from tiktokapipy.models.video import Video
import asyncio
import os
import io
from .. import loader, utils
import telethon
import urllib.request
import aiohttp

@loader.tds
class TikTokdlMod(loader.Module):
    """Download tiktok videos"""
    
    strings = {"name": "TikTokdl",
               "downloading": "Downloading from TikTok...",
               "uploading": "Uploading file...",
               "args_err": "Type URL or reply to a message with only url in it"}
    
    async def client_ready(self, client, db):
        self.client = client
    
    @loader.unrestricted
    @loader.ratelimit
    async def ttdlcmd(self, message):
        """.ttdl <url> or <reply> - download tiktok video from url"""
        
        text = utils.get_args_raw(message)
        if not text:
            if message.is_reply:
                text = (await message.get_reply_message()).message
            else:
                await utils.answer(message, self.strings("args_err", message))
                return
        
        # notify user we are here ♥
        await utils.answer(message, self.strings("downloading", message))
        
        async with AsyncTikTokAPI() as api:
            video = await api.video(text)
            if video.image_post:
                downloaded = await save_slideshow(video)
            else:
                downloaded = await save_video(video)
        
        #let user know we are done downloading
        await utils.answer(message, self.strings("uploading", message))
        #upload to telegram chat
        await self.client.send_file(message.to_id, downloaded)
        
        #delete original message
        await message.delete()

async def save_video(video: Video):
    async with aiohttp.ClientSession() as session:
        async with session.get(video.video.download_addr) as resp:
            o = io.BytesIO(await resp.read())
            o.name = "video.mp4"
            return o

async def save_slideshow(video: Video):
    for i, image_data in enumerate(video.image_post.images):
        url = image_data.image_url.url_list[-1]
        # this step could probably be done with asyncio, but I didn't want to figure out how
        urllib.request.urlretrieve(url, os.path.join("tiktok_cache", f"temp_{video.id}_{i:02}.jpg"))
    
    ret = []
    for i in os.listdir("tiktok_cache"):
        with open(os.path.join("tiktok_cache", i), "rb") as f:
            o = io.BytesIO(f.read())
        o.name = f"image{len(ret)}.jpg"
        ret.append(o)
    
    await clean_files()

    return ret

async def clean_files():
    #linux
    if os.name == "posix":
        return os.system("rm -rf tiktok_cache/*")
    #windows
    elif os.name == "nt":
        return os.system(r"del /Q .\tiktok_cache\*")