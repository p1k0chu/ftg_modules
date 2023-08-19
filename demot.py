import io, textwrap
from PIL import Image, ImageDraw, ImageFont
from telethon.tl.types import DocumentAttributeFilename
from uniborg.util import admin_cmd
from datetime import datetime
from asyncio import sleep
from .. import loader, utils
import telethon
import logging
logger = logging.getLogger(__name__)


async def register(cb):
    cb(DemoterMod())


@loader.tds
class DemoterMod(loader.Module):
    """Демотиваторы"""
    strings = {
        "name": "Demoter",
        "args_err": '<b>ТЕКСТА-ТО НЕТ АЛО</b>',
        "reply_err": '<b>РЕПЛАЙ НА ФОТО ИЛИ СТИКЕР</b>'
    }

    async def client_ready(self, client, db):
        self.client = client

    async def demotcmd(self, message):
        """.demot <text> - use with reply, demotivator"""
        
        await message.delete()
        
        text = utils.get_args_raw(message)
        if not text:
            await utils.answer(self.strings("args_err", message))
            return
        if message.is_reply:
            reply = await message.get_reply_message()
            data = await check_media(reply)
            
            # if message is not picture or sticker
            if isinstance(data, bool):
                await utils.answer(self.strings("reply_err", message))
                return
        else:
            await message.edit(self.strings("reply_err", message))
            return
            
        image = io.BytesIO()
        await self.client.download_media(data, image)
        image = Image.open(image)
        
        #apply demot
        image = await demot(text, image)
        
        #convert to jpeg
        fried_io = io.BytesIO()
        fried_io.name = "image.jpeg"
        image.save(fried_io, "JPEG")
        fried_io.seek(0)
        
        #send result picture
        await self.client.send_file(message.to_id, fried_io, reply_to=reply.id)



async def textpic(text):
    temp = ImageDraw.Draw(Image.new("RGB", (0, 0), "red"))
    color = (0, 0, 0, 0)
    
    if "&" in text:
        text = text.split("&", 1)
        utext, dtext = text
        utext, dtext = utext.replace('\n', ' '), dtext.replace('\n', ' ')
        utext = "\n".join(textwrap.wrap(utext.strip(), 65))
        dtext = "\n".join(textwrap.wrap(dtext.strip(), 60))
        ufont = ImageFont.truetype(size=100)
        dfont = ImageFont.truetype(size=80)
        uts = temp.multiline_textbbox((0, 0), utext.replace(' ', '\n'), font=ufont)
        uts = (uts[2]-uts[0], uts[3]-uts[1])
        dts = temp.multiline_textbbox((0, 0), dtext.replace(' ', '\n'), font=dfont)
        dts = (dts[2]-dts[0], dts[3]-dts[1])
        y = uts[1] + 30 + dts[1]
        x = max(uts[0], dts[0])
        #print(x, uts, dts)
        img = Image.new("RGBA", (x, y + 10), color)
        draw = ImageDraw.Draw(img)
        draw.multiline_text(((x - uts[0]) / 2, -10), utext.replace(' ', '\n'), fill="white", font=ufont, align="center")
        draw.multiline_text(((x - dts[0]) / 2, uts[1]+5), dtext.replace(' ', '\n'), fill="white", font=dfont, align="center")
    else:
        text = text.replace('\n', ' ')
        utext = "\n".join(textwrap.wrap(text, 60))
        ufont = ImageFont.truetype(io.BytesIO(demotfont), size=100)
        l, t, r, b = temp.multiline_textbbox((0, 0), utext.replace(' ', '\n'), font=ufont)
        x, y = r - l, b - t
        img = Image.new("RGBA", (x, y + 50), color)
        draw = ImageDraw.Draw(img)  
        draw.multiline_text((0, 0), utext.replace(' ', '\n'), fill="white", font=ufont, align="center")
    img.thumbnail((550, 9 ** 9), Image.LANCZOS)
    text = Image.new("RGBA", (650, img.height), (0, 0, 0, 0))
    text.paste(img, ((650 - img.width) // 2, 0), img)
    return text


async def template(image):
    image = image.resize((547, 397))
    demo = Image.new("RGB", (650, 500), 'black')
    draw = ImageDraw.Draw(demo)
    draw.rectangle((48, 48, 602, 452), fill=None, outline='white', width=2)
    demo.paste(image, (52, 52))
    return demo


async def demot(text, image):
    demot = await template(image)
    vator = await textpic(text)
    demotivator = Image.new("RGB", (650, 470 + vator.height), "black")
    demotivator.paste(demot, (0, 0))
    demotivator.paste(vator, (0, 460))
    return demotivator


async def check_media(reply):
    if reply and reply.media:
        if reply.photo:
            data = reply.photo
        elif reply.document:
            if DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in reply.media.document.attributes:
                return False
            if reply.gif or reply.video or reply.audio or reply.voice:
                return False
            data = reply.media.document
        else:
            return False
    else:
        return False

    if not data or data is None:
        return False
    else:
        return data