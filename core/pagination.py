import discord

from collections import deque
from typing import List

class PaginatedView(discord.ui.View):
	def __init__(self, embeds: List[discord.Embed]) -> None:
		super().__init__(timeout=45)

		self.embeds = embeds
		self.embed_queue = deque(embeds)
		self.start = embeds[0]
		self.len = len(embeds)
		self.current_embed = 0

	def button(self, rotate) -> discord.Embed:
		self.embed_queue.rotate(rotate)
		embed = self.embed_queue[0]
		return embed

	@discord.ui.button(label="Prev")
	async def previous(self, interaction: discord.Interaction, _):
		await interaction.response.edit_message(embed=self.button(-1))

	@discord.ui.button(label="Next")
	async def next(self, interaction: discord.Interaction, _):
		await interaction.response.edit_message(embed=self.button(1))

	async def on_timeout(self) -> None:
		for item in self.children:
			item.disabled = True

		await self.message.edit(view=self)

	@property
	def initial(self) -> discord.Embed:
		return self.embeds[0]
