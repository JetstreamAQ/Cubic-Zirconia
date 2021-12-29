import os
import discord
import urllib
import re
import yt_dlp
import asyncio

from discord.ext import commands, tasks
from discord import Embed, FFmpegPCMAudio, PCMVolumeTransformer
from yt_dlp import YoutubeDL
from queue import Queue

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}
YTDL_OPTIONS = {'extractaudio': True, 'format': 'bestaudio'}

class Audio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.activeServers = []
        self.queue = {}

        self.check_channels.start()
        print("[DEBUG] Audio Cog loaded")

    @tasks.loop(minutes=10.0)
    async def check_channels(self):
        for ids in self.activeServers:
            await self.empty_channel(self.bot.get_guild(ids).voice_client, self.bot.get_guild(ids).voice_client.channel.members)

    async def empty_channel(self, vc, channelMembers):
        if len(channelMembers) < 1:
            asyncio.sleep(120)
            if len(channelMembers) < 1:
                await vc.disconnect()

        if not self.voice_client.is_playing():
            asyncio.sleep(120)
            if not self.voice_client.is_playing():
                await vc.disconnect()

    async def add_to_queue(self, guildID, search):
        search = search.replace(" ", "+")
        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())

        video = "https://www.youtube.com/watch?v=" + video_ids[0]

        if guildID not in self.queue:
            self.queue[guildID] = Queue(maxsize = 0)
        self.queue.get(guildID).put(video)

    async def vc_play(self, ctx, link, vc):
        with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ytdlp:
            info = ytdlp.extract_info(link, download = False)
            url = info['formats'][3]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            vc.play(source, after = lambda e: asyncio.run(self.play_next(ctx)))

    async def play_next(self, ctx):
        vc = discord.utils.get(self.bot.voice_clients, guild = ctx.guild)

        if self.queue.get(ctx.message.guild.id).qsize() >= 1:
            if vc.is_playing():
                vc.stop()

            link = self.queue.get(ctx.message.guild.id).get()
            await self.vc_play(ctx, link, vc)
        

    @commands.command(name="play", description="Join current VC and play first result from youtube")
    async def play(self, ctx, search = ""):
        if (ctx.message.author.voice == None):
            await ctx.send("You must be in a voice channel first.")
            return
        elif not search and not self.queue.get(ctx.message.guild.id):
            await ctx.send("There's nothing for me to play.")
            return
        
        channel = ctx.message.author.voice.channel
        voice = discord.utils.get(ctx.guild.channels, name = channel.name)
        vc = discord.utils.get(self.bot.voice_clients, guild = ctx.guild)

        #Join the VC of the command issuer
        if vc is None:
            vc = await voice.connect()
        else:
            await ctx.send("I'm already playing something.")
            return
            #await vc.move_to(channel)

        link = ""
        if not self.queue.get(ctx.message.guild.id):
            await self.add_to_queue(ctx.message.guild.id, search)
        link = self.queue.get(ctx.message.guild.id).get()

        await ctx.send("Now playing: " + link)            
        await self.vc_play(ctx, link, vc)

        if (ctx.message.guild.id not in self.activeServers):
            self.activeServers.append(ctx.message.guild.id)

    @commands.command(name="queue", description="Add a video to the queue")
    async def queue(self, ctx, search):
        await self.add_to_queue(ctx.message.guild.id, search)
        videoQueue = self.queue.get(ctx.message.guild.id)
        await ctx.send("Queued: " + videoQueue.queue[videoQueue.qsize() - 1])

    @commands.command(name="next", description="Skip to the next video in the queue")
    async def next(self, ctx):
        vc = discord.utils.get(self.bot.voice_clients, guild = ctx.guild)
        if not vc.is_playing() or vc is None:
            await ctx.send("I'm not playing anything right now.")
            return

        await self.play_next(ctx)

    @commands.command(name="stop", description="Pause the current video")
    async def pause(self, ctx):
        vc = discord.utils.get(self.bot.voice_clients, guild = ctx.guild)

        if not vc.is_playing() or vc is None:
            await ctx.send("Pausing...")
            vc.pause()
        else:
            await ctx.send("I'm not playing anything right now.")

    @commands.command(name="resume", description="Resume the paused video")
    async def resume(self, ctx):
        vc = discord.utils.get(self.bot.voice_clients, guild = ctx.guild)

        if not vc.is_playing() or vc is None:
            await ctx.send("Resuming...")
            vc.resume()
        else:
            await ctx.send("I'm not playing anything right now.")

def setup(bot):
    bot.add_cog(Audio(bot))
