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
				"processing": "<b>Looking for Instagram Post...</b>",
				"uploading": "<b>Uploading files...</b>"}
	
	def __init__(self):
		self.il = instaloader.Instaloader()
	
	async def client_ready(self, client, db):
		self.client = client
	
	@loader.unrestricted
	@loader.ratelimit
	async def instacmd(self, message):
		""".insta <shortcode> - download post by shortcode"""
		
		args = utils.get_args(message)
		
		#there should be only one argument
		if len(args) != 1:
			await utils.answer(message, self.strings("args_err", message))
			return
		
		#TODO url parsing
		
		#let user know you handle command
		await utils.answer(message, self.strings("processing", message))
		
		post = instaloader.Post.from_shortcode(self.il.context, args[0])
		
		#let user know you downloading files
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
			await utils.answer(message, self.strings("uploading", message))
			#upload files
			await self.client.send_file(message.to_id, resources)
			#delete original message
			await message.delete()
		else:
			#idk why but cache folder has no media files
			#report if this happens
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
	return x.endswith(".jpg") or x.endswith(".mp4") or x.endswith(".jpeg") or x.endswith(".png") or x.endswith(".gif") or x.endswith(".mp4")
