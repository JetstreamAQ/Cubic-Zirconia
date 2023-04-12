import os
import json
import random
import re

from datetime import datetime
from discord.ext import commands, tasks
#from discord_slash import cog_ext, SlashContext

########
# PICKING A RANDOM PRODUCT FROM THE SCRAPED LIST!
########
def item_pick():		
	data = []
	locations = {
		0: "https://www.amazon.com"
	}

	try:
		for filename in sorted(os.listdir('./scraper/crawler')):
			if filename.endswith('.json'):
				with open(f'scraper/crawler/{filename}') as file:
					data.append(json.load(file))
	except ValueError:
		print("[WARNING] JSON file missing.  Is a manual scrape in progress?")
	
	#dataType = random.randint(0, (len(data) - 1)) #picking a web domain
	chosenData = random.choice(data[0]) #picking a random location within said web domain
	#some page scrapes return empty "url" definitions
	while not chosenData.get("url"):
		print("[DEBUG] Chosen listing is an empty URL.	Choosing again. ")
		chosenData = random.choice(data[dataType])
		print("[DEBUG] Valid listing chosen.")

	#grabbing the URL and splicing it with the domain if necessary
	chosenProduct = random.choice(chosenData.get("url"))
	resPart = "https://www.amazon.com" if chosenProduct.startswith("/") else ""
	result = resPart + chosenProduct
	return result

########
# Writing to JSON
########
def write_file(data):
	with open('recSettings.json', 'w', encoding='utf-8') as output:
		json.dump(data, output, ensure_ascii=False, indent=4)

########
# Checking if the command issuer is the bot owner
########
async def check_owner(ctx):
	ownerID = int(os.getenv('OWNER_ID'))
	if ctx.author.id != ownerID:
		await ctx.send('{}, you don\'t have permission to use this command.'.format(ctx.message.author.mention))
		return 1

	return 0

#######
# Appending new server data
######
def new_server(settings, guildID):
	messageDict = settings.get('recommend')
	if guildID not in messageDict.get('currentCount'):
		print("[DEBUG]: New Server.  Adding entries to JSON.")
		messageDict.get('maxMessage')[guildID] = 9
		messageDict.get('currentCount')[guildID] = 0
		messageDict.get('lastScrape')[guildID] = str(datetime.now())
		messageDict.get('interject')[guildID] = True
		
		write_file(settings)

# I should probably move the above functions for form, but I'm too lazy to rn

##################################################################
##################################################################
###															   ###
###					   THE ACTUAL COG CLASS					   ###
###								   							   ###
##################################################################
##################################################################
class Recommend(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		#loading server settings from JSON
		self.settings = {}
		if os.path.isfile('recSettings.json') and os.access('recSettings.json', os.R_OK):
			with open('recSettings.json') as file:
				self.settings = (json.load(file))
		else:
			print("[INFO]: JSON file missing or unreadable.  Creating new JSON.")
			masterServer = os.getenv('MASTER_SERVER_ID')
			self.settings ={
				'recommend': {
					'maxMessage': {
						masterServer: 24
					},
					'currentCount': {
						masterServer: 0
					},
					'lastScrape': {
						masterServer: str(datetime.now())
					},
					'interject': {
						masterServer: True
					}
				}
			}
			write_file(self.settings)

		#self.auto_crawl.start() #initiate auto_crawl background task

		print("[DEBUG] Recommendation Cog loaded")

	########
	# BACKGROUND EVENT: RUN THE SPIDER EVERY MONTH FROM THE LAST CRAWL
	########
	@tasks.loop(minutes=60.0)
	async def auto_crawl(self):
		#Check elapsed time from last scrape in master server
		masterServer = os.getenv('MASTER_SERVER_ID')
		oldTime = self.settings.get("recommend").get("lastScrape").get(masterServer)
		oldStrp = datetime.strptime(oldTime, "%Y-%m-%d %H:%M:%S.%f")
		timeDelta = (datetime.now() - oldStrp).days
		if (timeDelta < 30): #30 days
			return

		self.settings.get("recommend").get("lastScrape")[masterServer] = str(datetime.now())
		write_file(self.settings)
		print("[SYSTEM] Month since last scrape.  Initiating Re-Scrape.")
		os.system('scraper/runSpider.sh')

	########
	# initiateCrawl: FORCE THE BOT TO RUN THE SPIDER
	########
	@commands.command(name="initiateCrawl", description="Forces a crawl for updated product listings.", aliases=['ic'], hidden=True)
	async def force_crawl(self, ctx):
		if await check_owner(ctx) == 1:
			return

		self.settings.get("recommend").get("lastScrape")[str(ctx.message.guild.id)] = str(datetime.now())
		write_file(self.settings)
		print("[SYSTEM] Web Crawl forcefully initiated.")
		os.system('scraper/runSpider.sh')

	########
	# messageGap: HOW LONG UNTIL THE THING INTERJECTS
	########
	@commands.command(name="messageGap", description="How many messages until a product plug? DEF.: 25", aliases=['mg'])
	async def interject_cd(self, ctx, num):
		new_server(self.settings, str(ctx.message.guild.id))

		try:
			if isinstance(int(num), int):
				self.settings.get("recommend").get("maxMessage")[str(ctx.message.guild.id)] = abs(int(num)) - 1
				write_file(self.settings)

				print("[UPDATE] Interjection Interval has been changed >> " + '{}'.format(abs(int(num))))
				await ctx.send("Interjection interval updated.")
		except ValueError:
			print("[DEBUG] Interjection interval change attempt made.  Invalid arguement given.")
			await ctx.send("Provided arguement is not an integer.  Please try again and provide an integer arguement.")

	@interject_cd.error
	async def interject_cd_error(self, ctx, error):
		await ctx.send("Invalid arguments given.  Refer to +help for more information.")

	########
	# recommend: GENERATE A RECOMMENDATION
	########
	@commands.command(name="recommend", description="Get a random recommendation.", aliases=['rec', 'r'])
	async def item_recommend_c(self, ctx):
		new_server(self.settings, str(ctx.message.guild.id))		

		productURL = item_pick()
		await ctx.send("Here's a product you may enjoy: " + productURL)

	"""
	@cog_ext.cog_slash(name="recommend", description="Get a random recommendation.")
	async def item_recommend(self, ctx: SlashContext):
		productURL = item_pick()
		await ctx.send("Here's a product you may enjoy: " + productURL)
	"""

	########
	# interjectToggle: DISABLE INTERJECTIONS
	########
	@commands.command(name="interjectToggle", description="Disables bot interjections", aliases=['id'])
	async def interject_toggle(self, ctx):
		stringID = str(ctx.message.guild.id)
		interject = self.settings.get("recommend")
		new_server(self.settings, stringID)

		interject.get('interject')[stringID] = False if interject.get('interject')[stringID] else True
		write_file(self.settings)

		await ctx.send("Interjections enabled." if interject.get("interject")[stringID] else "Interjections disabled.")

	########
	# ON LISTENER FOR MESSAGES
	########
	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author == self.bot.user:
			return

		messageDict = self.settings.get("recommend")
		guildID = str(message.guild.id)

		new_server(self.settings, guildID)

		"""
		if guildID not in messageDict.get("currentCount"):
			print("[DEBUG]: New server, adding it to settings file.");
			messageDict.get('maxMessage')[guildID] = 9
			messageDict.get('currentCount')[guildID] = 0
			messageDict.get('lastScrape')[guildID] = str(datetime.now())
		"""

		currentCount = messageDict.get("currentCount").get(guildID)
		curCountMut = messageDict.get("currentCount")
		maxMessage = messageDict.get("maxMessage").get(guildID)
		
		if maxMessage <= 0 or messageDict.get('interject').get(guildID):
			return
		elif currentCount >= maxMessage:
			print("[STATUS] Message count cap reached.	Making interjection.")
			curCountMut[guildID] = 0
			words = re.findall(r'\b\w+\b', message.content)
			productURL = item_pick()

			try:
				await message.channel.send(
					"I'm terribly sorry to interrupt you right now, but I couldn't help myself from interjecting.  " +
					"That being said, I happened to overhear that you've mentioned: [" + random.choice(words) + "]!  " +
					"And we just so happen to have something you may be very interested in as a result!  Behold: " +
					productURL
				)
			except IndexError:
				await message.channel.send(
					"I'm terribly sorry to interrupt you right now, but I couldn't help myself from interjecting.  " +
					"That being said, I happened to overhear you just then.  And right now, we happen to have something " +
					"in stock that you may be interested in!  Behold: " + productURL
				)
			
			write_file(self.settings)
		else:
			curCountMut[guildID] += 1
			write_file(self.settings)

async def setup(bot):
	await bot.add_cog(Recommend(bot))
