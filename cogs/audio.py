import os
import pafy
import discord
import urllib
import re

from discord.ext import commands, tasks
from discord import Embed, FFmpegPCMAudio, PCMVolumeTransformer

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

class Audio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.activeServers = [];
        print("[DEBUG] Audio Cog loaded")

    @tasks.loop(minutes=10.0)
    async def check_channels(self):
        for ids in self.activeServers:
            await empty_channel(self.bot.get_guild(id).voice_client, self.bot.get_guild(ids).voice_client.channel.members)

    async def empty_channel(vc, channelMembers):
        if len(channelMembers) < 1:
            asyncio.sleep(120)
            if len(channelMembers) < 1:
                await vc.disconnect()

    @commands.command(name="play", description="Join current VC and play first result from youtube")
    async def play(self, ctx, search):
        if (ctx.message.author.voice == None):
            await ctx.send("You must be in a voice channel first.")
            return

        channel = ctx.message.author.voice.channel
        voice = discord.utils.get(ctx.guild.channels, name = channel.name)
        vc = discord.utils.get(self.bot.voice_clients, guild = ctx.guild)

        #Join the VC of the command issuer
        if (vc == None):
            vc = await voice.connect()
        else:
            await vc.move_to(channel)

        search = search.replace(" ", "+")

        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())

        await ctx.send("https://www.youtube.com/watch?v=" + video_ids[0])

        try:
            song = pafy.new(video_ids[0])
        except OSError:
            await ctx.send("This video is age restricted!  I'm unable to get fetch it for you.")
            return
        audio = song.getbestaudio()  # gets an audio source
        source = FFmpegPCMAudio(audio.url, **FFMPEG_OPTIONS)  # converts the youtube audio source into a source discord can use
        vc.play(source)  # play the source

        if (ctx.message.guild.id not in self.activeServers):
            self.activeServers.append(ctx.message.guild.id)

def setup(bot):
    bot.add_cog(Audio(bot))
