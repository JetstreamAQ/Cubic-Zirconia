import os
import json
import random
import discord

from core.pagination import PaginatedView
from discord.ext import commands, tasks
from discord.interactions import Interaction
from discord import Embed
from datetime import datetime 

########
# Writing to JSON
#######
def write_file(data, data2):
	with open('stockSettings.json', 'w', encoding='utf-8') as output:
		json.dump(data, output, ensure_ascii=False, indent=4)

	with open('userData.json', 'w', encoding='utf-8') as output:
		json.dump(data2, output, ensure_ascii=False, indent=4)

##################################################################
##################################################################
###															   ###
###					   THE ACTUAL COG CLASS					   ###
###															   ###
##################################################################
##################################################################
class Stocks(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.settings = []
		with open('stockSettings.json') as file:
			self.settings = (json.load(file))	
	
		self.userData = []
		if os.path.isfile('userData.json') and os.access('userData.json', os.R_OK):
			with open('userData.json') as file:
				self.userData = (json.load(file))
		else:
			print("[INFO]: userData.json missing or unreadable.  Creating new JSON.")
			masterServer = os.getenv('MASTER_SERVER_ID')
			owner = os.getenv('OWNER_ID')
			self.userData = {
				"playerData": {
					masterServer: {
						owner: {
							"investedCommodities": {},
							"investedStocks": {},
							"money": 1000.0
						}
					}
				}
			}
			write_file(self.settings, self.userData)


		self.price_update.start()

		print("[DEBUG] Stocks Cog loaded")

	########
	# updating the stock data (sales)
	########
	def sales_update(self, item, investType, numBought):
		itemType = "commodities" if investType == "investedCommodities" else "stocks"
		data = self.settings.get("stockSales").get(itemType)
		
		if item not in data:
			data[item] = numBought
			return

		data[item] += numBought

	########
	# BACKGROUND EVENT: Update the stock price roughly every half-hour (SYSTEM TIME)
	########
	@tasks.loop(minutes=1.0)
	async def price_update(self):
		#Time check
		oldTime = self.settings.get("lastCheck")
		oldStrp = datetime.strptime(oldTime, "%Y-%m-%d %H:%M:%S.%f")
		# Doing it this way to get somewhat more exact 30 minute intervals
		# Side-effect of doing it this way is more noticable for a tasks.loop.minutes value > 1 that get closer to 30
		# Essentially allows for that value to be easily increased if 1 minute intervals are too frequent
		timeDelta = (datetime.now() - oldStrp).seconds / 3600
		if (timeDelta < 0.5):
			return

		#Modifying stock data (prices, and old data)
		currentPrices = self.settings.get("stockData")
		oldPrices = self.settings.get("oldStockData")
		deltaPrices = self.settings.get("stockChanges")
		saleData = self.settings.get("stockSales")
		volatiles = set(self.settings.get("volatiles"))
		for itemType in currentPrices:
			for item in currentPrices.get(itemType):
				#create data entry for new stock if it hasn't been bought yet
				if item not in saleData.get(itemType):
					saleData.get(itemType)[item] = 0
				
					#new difference
					deltaPrices.get(itemType)[item] = 0

				#new price
				roll = random.randint(0, 100)
				weightMod = 0
				deltaLowerLimit, deltaUpperLimit = 0.0, 32.0
				if item in volatiles:
					weightMod = -30 if (saleData.get(itemType).get(item) / 1000 < 10) else -10
					deltaLowerLimit, deltaUpperLimit = 25.0, 1500.0 if (roll > 50 + weightMod) else 3000.0
				else:
					demandBonus = saleData.get(itemType).get(item) / 1000
					negativeBonus = 0 if (currentPrices.get(itemType).get(item) >= 0) else 10
					totalBonus = demandBonus + negativeBonus
					weightMod = 40 if (50 + totalBonus > 90) else -40 if (50 - totalBonus < 10) else totalBonus

				changeDir = 1 if (roll <= (50 + weightMod)) else -1
				oldPrices.get(itemType)[item] = currentPrices.get(itemType).get(item)
				priceDelta = float(changeDir) * random.uniform(deltaLowerLimit, deltaUpperLimit)
				newPrice = currentPrices.get(itemType).get(item) + priceDelta
				currentPrices.get(itemType)[item] = newPrice if newPrice >= -500.00 else -500.00
				deltaPrices.get(itemType)[item] = currentPrices.get(itemType).get(item) - oldPrices.get(itemType).get(item)
				saleData.get(itemType)[item] = 0

				#saves the last time stock data was edited
				self.settings["lastCheck"] = str(datetime.now())
				write_file(self.settings, self.userData)
	
	########
	# checking if the server/player exists in the current database
	########
	def db_check(self, ctx):
		if str(ctx.guild.id) not in self.userData.get("playerData"):
			self.userData.get("playerData")[str(ctx.guild.id)] = {
				str(ctx.author.id): {
					'investedCommodities': {},
					'investedStocks': {},
					'money': 1000.00
				}
			}
			write_file(self.settings, self.userData)
	
		if str(ctx.author.id) not in self.userData.get("playerData").get(str(ctx.guild.id)):
			self.userData.get("playerData").get(str(ctx.guild.id))[str(ctx.author.id)] = {
				'investedCommodities': {},
				'investedStocks': {},
				'money': 1000.00
			}
			write_file(self.settings, self.userData)

	########
	# invest: Make an investment
	########
	#still looks like AIDS
	async def p_check(self, ctx, item, investType, total, num):
		portfolio = self.userData.get("playerData").get(str(ctx.guild.id)).get(str(ctx.author.id))			
		author = ctx.message.author.mention

		if portfolio.get("money") >= total:
			current = portfolio.get(investType).get(item) if portfolio.get(investType).get(item) is not None else 0
			stocksNum = num + int(current)
			portfolio.get(investType)[item] = stocksNum
			portfolio["money"] -= total
		else:
			await ctx.send('{}'.format(author) + "!  You don't have enough money to buy the stocks you wish to buy!")
			return

		self.sales_update(item, investType, num)


		unitType = "unit" if investType == "investedCommodities" else "share"
		await ctx.send(
			str(num) + 
			" " + unitType + "(s) of **" + item + "** have been bought for " + 
			'${:,.2f}'.format(total) +
			' by {}'.format(author)
		)

	@commands.command(name="invest", description="Buy [num] shares of [name (in quotes if there are spaces)])", aliases=['i', 'I'])
	async def make_investment(self, ctx, stock, num):
		self.db_check(ctx)

		portfolio = self.userData.get("playerData").get(str(ctx.guild.id)).get(str(ctx.author.id))
		data = self.settings.get("stockData")
		if stock not in data.get("commodities") and stock not in data.get("stocks"):
			await ctx.send(
				'{}!  '.format(ctx.message.author.mention) +
				"The desired stock does not exist at the moment... Use **+stockPrices** for available stocks!  " +
				"Also, make sure that the name is incased in quotation marks if there are multiple words in it!"
			)
			return

		pricePer = data.get("commodities").get(stock) if stock in data.get("commodities") else data.get("stocks").get(stock)
		if pricePer <= 0:
			await ctx.send("The requested stock is currently delisted, " + '{}'.format(ctx.message.author.mention))
			return

		processedNum = num
		bal = portfolio.get("money")
		var = {"max": 1, "half": 2, "quarter": 4, "fourth": 4}
		if type(num) == str and num.lower() in var:
			processedNum = (bal / var.get(num.lower())) / pricePer
		elif not num.isnumeric():
			await ctx.send(
				"The passed quantity is not valid, " + 
				'{}'.format(ctx.message.author.mention) +
				".  Accepted quantities are whole number strings composed of only digits.  " +
				"You may also pass either: MAX, HALF, QUARTER or FOURTH as a quantity instead."
			)
			return

		if int(processedNum) <= 0:
			await ctx.send(
				'{}'.format(ctx.message.author.mention) + 
				", you can not make a purchase of amount: " + processedNum + "."
			)
			return

		investType = "investedCommodities" if stock in data.get("commodities") else "investedStocks"
		totalPrice = pricePer * abs(float(processedNum))
		await self.p_check(ctx, stock, investType, totalPrice, abs(int(processedNum)))
		write_file(self.settings, self.userData)

	########
	# sell: sell some stocks
	########
	async def s_check(self, ctx, item, investType, total, num):
		portfolio = self.userData.get("playerData").get(str(ctx.guild.id)).get(str(ctx.author.id))
		author = ctx.message.author.mention
		current = portfolio.get(investType).get(item)

		if num < current:
			stocksNum = current - num
			portfolio.get(investType)[item] = stocksNum
			portfolio["money"] += total
		elif num == current:
			del portfolio.get(investType)[item]
			portfolio["money"] += total
		else:
			await ctx.send('{}!  '.format(author) + "You can't sell more than you have!")
			return
		
		self.sales_update(item, investType, -num)

		unitType = "unit" if investType == "investedCommodities" else "share"
		await ctx.send(
			str(num) + 
			" " + unitType + "(s) of **" + item + " **have been sold for " + 
			'${:,.2f}'.format(total) + 
			' by {}'.format(author)
		)

	@commands.command(name="sell", description="Sell [num] shares of [name (in quotes if there are spaces)]", aliases=['s', 'S'])
	async def make_sale(self, ctx, stock, num):
		self.db_check(ctx)

		portfolio = self.userData.get("playerData").get(str(ctx.guild.id)).get(str(ctx.author.id))
		data = self.settings.get("stockData")
		if stock not in portfolio.get("investedCommodities") and stock not in portfolio.get("investedStocks"):
			await ctx.send("You can't sell something you don't own," + ' {}'.format(ctx.message.author.mention))
			return
		
		## section here function exactly like the last portion in 
		pricePer = data.get("commodities").get(stock) if stock in data.get("commodities") else data.get("stocks").get(stock)
		if pricePer <= 0:
			await ctx.send("The requested stock is currently delisted, " + '{}'.format(ctx.message.author.mention))
			return

		processedNum = num
		investType = "investedCommodities" if stock in data.get("commodities") else "investedStocks"
		current = portfolio.get(investType).get(stock)
		var = {"max": 1, "half": 2, "quarter": 4, "fourth": 4}
		if type(num) == str and num.lower() in var:
			processedNum = (current / var.get(num.lower()))
		elif not num.isnumeric():
			await ctx.send(
				"The passed quantity is not valid, " + 
				'{}'.format(ctx.message.author.mention) +
				".  Accepted quantities are whole number strings composed of only digits.  " +
				"You may also pass either: MAX, HALF, QUARTER or FOURTH as a quantity instead."
			)
			return

		if int(processedNum) <= 0:
			await ctx.send(
				'{}'.format(ctx.message.author.mention) + 
				", you can not make a sale of amount: " + processedNum + "."
			)
			return
		
		totalPrice = pricePer * abs(float(processedNum))
		await self.s_check(ctx, stock, investType, totalPrice, abs(int(processedNum)))
		write_file(self.settings, self.userData)

	########
	# portfolio: Grab the portfolio of the requester
	########
	@commands.command(name="portfolio", description="Request your investment portfolio", aliases=['p', 'P'])
	async def get_portfolio(self, ctx):
		self.db_check(ctx)

		infoString = ""
		portfolioData = self.userData.get("playerData").get(str(ctx.guild.id)).get(str(ctx.author.id))
		strings = {
			'investedCommodities': "__**Invested Commodities:**__ \n",
			'investedStocks': "\n__**Invested Stocks:**__ \n",
			'money': "\n__**Money**__: "
		}

		for key in portfolioData:
			if str(key) == "investedCommodities":
				infoString += (strings.get(key))
				commodityInvestments = ""
				for commodity in portfolioData.get(key):
					commodityInvestments += ("**" + commodity + ":** *" + str(portfolioData.get(key).get(commodity)) + "*\n")

				infoString += "*None*\n" if commodityInvestments == "" else commodityInvestments
			elif str(key) == 'investedStocks':
				infoString += (strings.get(key))
				stockInvestments = ""
				for stock in portfolioData.get(key):
					stockInvestments += ("**" + stock + ":** *" + str(portfolioData.get(key).get(stock)) + "*\n")
				
				infoString += "*None*\n" if stockInvestments == "" else stockInvestments
			else:
				infoString += (strings.get(key) + '${:,.2f}'.format(portfolioData.get(key)))

		p_embed = discord.Embed(title="Investment Portfolio", description=infoString, color = 0x00ff00)
		p_embed.set_author(name=ctx.author.display_name, url="", icon_url=ctx.author.display_avatar)
		await ctx.channel.send(embed=p_embed)

	########
	# stockPrices: Grab updated stock prices for the game
	########
	@commands.command(name="stockPrices", description="Request the (game) stock prices for today", aliases=['sp', 'sP', 'Sp', 'SP'])
	async def get_stock_prices(self, ctx):
		data = self.settings.get("stockData")
		delta = self.settings.get("stockChanges")

		c_listings = ""
		s_listings = ""
		for itemType in data:
			for item in data.get(itemType):
				if item not in delta.get(itemType):
					delta.get(itemType)[key] = 0.0

				dataString = (
					("<:green_triangle:862849832179597312> " if delta.get(itemType).get(item) >= 0 else ":small_red_triangle_down: ") +
					"__**" + item + ":**__ *" +
					'${:,.2f}'.format(data.get(itemType).get(item)) + "*\n"
				)
				
				if itemType == "commodities":
					c_listings += dataString
				else:
					s_listings += dataString

		#embed for commodities
		c_embed = discord.Embed(title="Commodities (Price per unit)", description=c_listings, color=0xff0000)
		c_embed.set_image(url="https://media.tenor.com/AbkJkB1pGr8AAAAi/hutao-money-rain.gif")

		#embed for stocks
		s_embed = discord.Embed(title="Stocks (Price per share)", description=s_listings, color=0x0000ff)
		s_embed.set_image(url="https://media.tenor.com/images/d8ac4e749942f31ddfb928dee86244d3/tenor.gif")

		#await ctx.channel.send(embed=c_embed)
		#await ctx.channel.send(embed=s_embed)
		embeds = [c_embed, s_embed]
		view = PaginatedView(embeds)
		view.message = await ctx.channel.send(embed=view.initial, view=view)
		#view.message = await interaction.original_response()

	########
	# stockRequests: Fetch the list of requests for this quarter
	########
	@commands.command(name="stockRequests", description="Fetch the current list of requests", aliases=['sr', 'Sr', 'sR', 'SR'])
	async def get_requests(self, ctx):
		companyList = list(self.settings.get("stockData").get("stocks"))
		commodityList = list(self.settings.get("stockData").get("commodities"))
		for company in companyList:
			if self.settings.get("stockData").get("stocks").get(company) > 0:
				companyList.remove(company)

		chosenCompanies = random.sample(companyList, 8)
		print(chosenCompanies)
		print(commodityList)

async def setup(bot):
	await bot.add_cog(Stocks(bot))
