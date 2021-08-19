import io
import PIL
from .. import loader, utils
import requests
import json
import telethon
import os


@loader.tds
class QuotesMod(loader.Module):
    """Quotes a message using Mishase Quotes API"""
    strings = {
        "name": "Quotes",
        "silent_processing_cfg_doc": ("Process quote "
                                      "silently(mostly"
                                      " w/o editing)"),
        "module_endpoint_cfg_doc": "Module endpoint URL",
        "quote_limit_cfg_doc": "Limit for messages per quote",
        "max_width_cfg_doc": "Maximum quote width in pixels",
        "scale_factor_cfg_doc": "Quote quality (up to 5.5)",
        "square_avatar_cfg_doc": "Square avatar in quote",
        "text_color_cfg_doc": "Color of text in quote",
        "reply_line_color_cfg_doc": "Reply line color",
        "reply_thumb_radius_cfg_doc": ("Reply media thumbnail "
                                       "radius in pixels"),
        "admintitle_color_cfg_doc": "Admin title color",
        "message_radius_cfg_doc": "Message radius in px",
        "picture_radius_cfg_doc": "Media picture radius in px",
        "background_color_cfg_doc": "Quote background color",
        "quote_limit_reached": ("The maximum number "
                                    "of messages in "
                                    "multiquote - {}."),
        "fq_incorrect_args": ("<b>Не корректные аргументы.</b> \"@$username (ID)"
                              "$text\" or \"$reply $text\""),
        "updating": "<b>Updating...</b>",
        "update_error": "<b>Update error</b>",
        "processing": "<b>Извиняюсь...</b>",
        "unreachable_error": "<b>API хост не доступен. Будешь без цитат.</b>",
        "server_error": "<b>Ошибка API :)</b>",
        "no_reply": "<b>Отвечать на сообщение!</b>",
        "creator": "Owner",
        "admin": "Admin",
        "channel": "Channel",
        "media_type_photo": "Photo",
        "media_type_video": "📹Video",
        "media_type_videomessage": "📹Video message",
        "media_type_voice": "🎵Voice message",
        "media_type_audio": "🎧Music: {} - {}",
        "media_type_contact": "👤Contact: {}",
        "media_type_poll": "📊Poll: ",
        "media_type_quiz": "📊Quiz: ",
        "media_type_location": "📍Location",
        "media_type_gif": "🖼GIF",
        "media_type_sticker": "Sticker",
        "media_type_file": "💾File",
        "dice_type_dice": "Dice",
        "dice_type_dart": "Dart",
        "ball_thrown": "Ball thrown",
        "ball_kicked": "Ball kicked",
        "dart_thrown": "Dart thrown",
        "dart_almostthere": "almost there!",
        "dart_missed": "missed!",
        "dart_bullseye": "bullseye!"
    }

    def __init__(self):
        self.config = loader.ModuleConfig("SILENT_PROCESSING", False,
                                          lambda: self.strings["silent_processing_cfg_doc"],
                                          "QUOTE_MESSAGES_LIMIT", 15,
                                          lambda: self.strings["quote_limit_cfg_doc"],
                                          "MAX_WIDTH", 384,
                                          lambda: self.strings["max_width_cfg_doc"],
                                          "SCALE_FACTOR", 5,
                                          lambda: self.strings["scale_factor_cfg_doc"],
                                          "SQUARE_AVATAR", False,
                                          lambda: self.strings["square_avatar_cfg_doc"],
                                          "TEXT_COLOR", "white",
                                          lambda: self.strings["text_color_cfg_doc"],
                                          "REPLY_LINE_COLOR", "white",
                                          lambda: self.strings["reply_line_color_cfg_doc"],
                                          "REPLY_THUMB_BORDER_RADIUS", 2,
                                          lambda: self.strings["reply_thumb_radius_cfg_doc"],
                                          "ADMINTITLE_COLOR", "#969ba0",
                                          lambda: self.strings["admintitle_color_cfg_doc"],
                                          "MESSAGE_BORDER_RADIUS", 10,
                                          lambda: self.strings["message_radius_cfg_doc"],
                                          "PICTURE_BORDER_RADIUS", 8,
                                          lambda: self.strings["picture_radius_cfg_doc"],
                                          "BACKGROUND_COLOR", "#162330",
                                          lambda: self.strings["background_color_cfg_doc"])

    async def client_ready(self, client, db):
        self.client = client

    @loader.unrestricted
    @loader.ratelimit
    async def fquotecmd(self, message):
        """.fquote @<username> <text> or <reply> <text> - fake quote"""
        if not self.config["SILENT_PROCESSING"]:
            mmm = await utils.answer(
                message,
                self.strings(
                    "processing",
                    message
                )
            )
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        spl_args = args.split(maxsplit=1)
        if len(spl_args) == 2 and (spl_args[0].startswith('@') or spl_args[0].isdigit()):
            user = spl_args[0][1:] if spl_args[0].startswith(
                '@') else int(spl_args[0])
            text = spl_args[1]
        elif reply:
            user = reply.sender_id
            text = " ".join(spl_args)
        else:
            await utils.answer(
                mmm,
                self.strings(
                    "fq_incorrect_args",
                    message
                )
            )
            return
        try:
            user = await self.client.get_entity(user)
            name = telethon.utils.get_display_name(user)
            avatar = await self.client.download_profile_photo(user.id, "mishase_cache/") if not str(user).isdigit() else \
                await self.client.download_profile_photo(user, "mishase_cache/")
        except:
            await utils.answer(
                mmm,
                self.strings(
                    "fq_incorrect_args",
                    message
                )
            )
            return
        files = []
        msg = {
            "text": text,
            "reply": None,
            "entities": [],
            "author": {
                "id": str(user.id) if not str(user).isdigit() else str(user),
                "name": name,
                "adminTitle": ' ',
            }
        }
        if avatar:
            msg['author']['picture'] = {
                'file': f'@av{str(user.id).lstrip("-")}'}
            files.append(("files", (
                f'@av{str(user.id if not str(user).isdigit() else user).lstrip("-")}', open(avatar, "rb"),
                "image/jpg")))
        else:
            files.append(("files", ("file", bytearray(), "text/text")))
        data = {
            "messages": [msg],
            "maxWidth": self.config["MAX_WIDTH"],
            "scaleFactor": self.config["SCALE_FACTOR"],
            "squareAvatar": self.config["SQUARE_AVATAR"],
            "textColor": self.config["TEXT_COLOR"],
            "replyLineColor": self.config["REPLY_LINE_COLOR"],
            "adminTitleColor": self.config["ADMINTITLE_COLOR"],
            "messageBorderRadius": self.config["MESSAGE_BORDER_RADIUS"],
            "replyThumbnailBorderRadius": self.config["REPLY_THUMB_BORDER_RADIUS"],
            "pictureBorderRadius": self.config["PICTURE_BORDER_RADIUS"],
            "backgroundColor": self.config["BACKGROUND_COLOR"],
        }
        try:
            req = await utils.run_sync(
                requests.post,
                "https://quotes.mishase.dev/create",
                data={"data": json.dumps(data), "moduleBuild": None},
                files=files,
                timeout=100
            )
        except (requests.ConnectionError, requests.exceptions.Timeout):
            await clean_files()
            return await utils.answer(
                mmm,
                self.strings("unreachable_error", message)
            )
        await clean_files()
        
        image = io.BytesIO()
        image.name = "fquote.webp"
        try:
            PIL.Image.open(io.BytesIO(req.content)).save(image, "WEBP")
            image.seek(0)
            return await utils.answer(mmm, image)
        except Exception as e:
            return await utils.answer(
                mmm,
                self.strings(
                    "server_error",
                    message
                )
            )


async def clean_files():
    return os.system("rm -rf mishase_cache/*")
