from .. import loader, utils
import telethon
import os
import instaloader

@loader.tds
class InstaLoaderMod(loader.Module):
	"""Downloads posts from instagram using InstaLoader"""
	strings = {"name": "InstaLoader",
				"args_err": "Smth is wrong with args",
				"downloading": "<b>Downloading Instagram Post...</b>",
				"loader_not_loading": "Something <i>strange</i> happened. Pls contact author @p1k0chu and send him link to the Instagram post caused this problem",
				"processing": "<b>Looking for Instagram Post...</b>"}
	
	def __init__(self):
		self.il = instaloader.Instaloader()
	
	async def client_ready(self, client, db):
		self.client = client
	
	@loader.unrestricted
	@loader.ratelimit
	async def instacmd(self, message):
		""".insta <shortcode> - download post by shortcode"""
		args = utils.get_args(message)
		
		if len(args) != 1:
			await utils.answer(message, self.strings("args_err", message))
			return
		
		await utils.answer(message, self.strings("processing", message))
		
		chat = await self.client.get_input_entity(message.to_id)
		self.client.action(chat, "photo")
		
		post = instaloader.Post.from_shortcode(self.il.context, args[0])
		
		await utils.answer(message, self.strings("downloading", message))
		
		self.il.download_post(post, "instaloader_cache")
		resources = list(filter(my_filter, ["instaloader_cache/"+i for i in os.listdir("instaloader_cache")]))
		
		if len(resources) >= 1:
			await message.delete()
			await self.client.send_file(message.to_id, resources)
		else:
			await utils.answer(message, self.strings("loader_not_loading", message))
		
		self.client.action(chat, "cancel")
		await clean_files()

async def clean_files():
	if os.name == "posix":
		return os.system("rm -rf instaloader_cache/*")
	elif os.name == "nt":
		return os.system(r"del /Q .\instaloader_cache\*")

def my_filter(x):
	return x.endswith(".jpg") or x.endswith(".mp4")
