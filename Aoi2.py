from sys import platlibdir
import typing
import discord
from discord import activity
import spotipy
import random
from discord import channel
from discord import client
from discord import player
from discord.enums import Status, TeamMembershipState
from discord.ext import commands, tasks
from random import choice
from discord.ext.commands import Bot
from discord.webhook import AsyncWebhookAdapter
from discord.voice_client import VoiceClient
from discord import FFmpegPCMAudio
import asyncio
import os
from discord.utils import _parse_ratelimit_header, get
import youtube_dl
import ffmpeg
from youtube_dl.utils import escape_url, lookup_unit_table
import spotdl

youtube_dl.utils.bug_reports_message = lambda:''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


stats = ['Killing people like chanda','hanging Children','torturing dingo','fucking dingo platonically']
queue_title = []
url = []

client = Bot(command_prefix=".")

@client.event
async def on_ready():
    change_status.start()
    print("ready")

@tasks.loop(seconds=3)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(stats)))


@client.command(__name__='join')
async def join(ctx):
    if(ctx.author.voice):
        channel = ctx.message.author.voice.channel
        voice= await channel.connect()
        #source = FFmpegPCMAudio('aud.mp3')
        #player = voice.play(source)
    else:
        await ctx.send("Master, please connect to a voice channel first")
    

@client.command(__name__='leave')
async def leave(ctx):
    if(ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send("I left the Vc master")
    else:
        await ctx.send("Master, I am not in a voice channel")

@client.command(__name_='pause')
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send(' No song is playing Master.')

def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    if voice.is_playing():
        voice.pause()
    

@client.command(__name_='resume')
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild= ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("No song is paused.")

@client.command(__name__='q')
async def q(ctx):
    global queue_title
    
    if queue_title != []:
        titles = ''
        for song in queue_title:
            titles+=song+'\n'

        await ctx.send("Master these are the titles \n {}".format(titles))
    else:
        await ctx.send("Master the queue is empty")
    

@client.command(__name__="remove")
async def remove(ctx, number):
    global url
    global queue_title

    try:
        del(queue_title[int(number)])
        del(url[int(number)])
        await ctx.send(f'Master this is the new queue_title `{queue_title}!`')
    
    except:
        await ctx.send('Master the queue_title is Empty, or you have entered an int which is out of index range')

def remove(number):
    global url
    global queue_title

    try:
        del(queue_title[int(number)])
        del(url[int(number)])
    except:
        print("array out of bound")

@client.command(__name__='play')
async def play(ctx, ur):
    global queue_title
    global url
    temp = []
    url.append(ur)
    

    
    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(url[0], loop=client.loop)
        if queue_title!=player.title:
            queue_title.append(player.title)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('Master, now playing {}'.format(player.title))
    
    del(url[0])
    del(queue_title[0])
    

@client.command(_name__='add')
async def add(ctx,ur):
    global queue_title
    global url
    url.append(ur)
    player = await YTDLSource.from_url(ur, loop=client.loop)
    queue_title.append(player.title)
    await ctx.send(f'{player.title} added to queue master')


@client.command(__name__='next')
async def next(ctx):
    global url
    pause(ctx)
    remove(0)
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            player = await YTDLSource.from_url(url[0], loop=client.loop)
            voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Master, now playing {}'.format(player.title))
        #del(url[0])
        del(queue_title[0])
    except:
        await ctx.send("Master it is an index out of bound error or either the queue_title is empty")


@client.command(__name__='jump')
async def jump(ctx,num):
    pause(ctx)
    global url
    item = num
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            player = await YTDLSource.from_url(url[item], loop = client.loop)
            voice_channel.play(player, after= lambda e:print('Player error: %s'%e)if e else None)
        
        await ctx.send("Master now playing {}".format(player.title))
        del(url[item])
        del(queue_title[item])
    except:
        await ctx.send('Master there is an imdex out of bound error')


@client.command(__name__="special")
async def special(ctx):
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
        source = FFmpegPCMAudio('Our Story Tieff.mp3')
        player = voice.play(source)
    else:
        await ctx.send("master please connect to a voice channel")


@client.command(__name__='clear')
async def clear(ctx):
    pause(ctx)
    global queue_title
    global url
    if url!=[] and queue_title!=[]:
        url.clear()
        queue_title.clear()

        await ctx.send('Master, I have cleared the list')


@client.command(__name__="music_help")
async def music_help(ctx):
    await ctx.send('At your sevice Master, please use theses commands to experiance a smooth listening experiance:-'+'\n'+'first use the join command'+'use play(url) to play and add the song to queue, note the somg will be deleted automatically after it is played'+"\n"+'use q to display the queue'+'\n'+'use remove or clear to delete the queue partially or completely'+'\n'+'use .next to skip a song in queue'+'\n'+"use jump, pause, resume to controll the song played")


client.run('ODgxNTM3NjY1OTQwNDg4MjEy.YSuR7Q.uRGMwUpr_oCLKnMO9VILjW88FmQ')