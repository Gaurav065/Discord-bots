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
import requests
import json


client = Bot(command_prefix = '_')

#on ready 
@client.event
async def on_ready():
        print('Ready to log in')

@client.command(__name__='Ping')
async def ping(ctx):
        await ctx.send(f"pong")

#Function which gets quotes through requests and converts it into a json for accessibility
def quotes():
        response = requests.get("https://animechan.vercel.app/api/random")
        json_data = json.loads(response.text)
        #quote = json_data[0]['anime'] + '\n' + json_data[0]['character']+'\n'+json_data[0]['quote']
        qu = 'anime:'+json_data['anime']+'\n'+json_data['quote']+'~'+json_data['character']
        return qu
        
        
        

@client.command(__name__='boost')
async def boost(ctx):
        quote = quotes()
        await ctx.send(quote)


client.run('ODc4MTAwNzQzNTE5ODY2ODgw.YR8RCw.NNuZFOQqKGqYLOK4zO_RVs9nyGY')