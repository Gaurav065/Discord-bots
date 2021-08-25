import os
import discord 
from discord.ext import commands
import random
from discord.flags import Intents
from discord.utils import get 
import requests 
import json
import random


client = commands.Bot(command_prefix = '.')

#on ready 
@client.event
async def on_ready():
        print('Ready to log in')

@client.event
async def on_member_join(member):
        print(f'{member} has joined the guild')

@client.event
async def on_member_remove(member):
        print(f'{member} has left the guild')

#Function which gets quotes through requests and converts it into a json for accessibility
def quotes():
        response = requests.get("https://zenquotes.io/api/random")
        json_data = json.loads(response.text)
        quote = json_data[0]['q'] + ' -' + json_data[0]['a']
        return(quote)

@client.event
async def on_message(self):
        if self.author == client.user:
                return('a user has sent a message')

        if self.content.startswith(".encourage"):
                quote = quotes()     
                await self.channel.send(quote)
                

#audio section 


#audio section
@client.command(pass_context= True)
async def reminder(ctx):
        channel = ctx.author.channel

        
@client.command()
async def join(ctx):
        channel = ctx.author.voice.channel
        await channel.connect()

@client.command(pass_context = 'leave')
async def leave(ctx):
        if (ctx.voice_client):
                await ctx.guild.voice_client.disconnect()
                await ctx.send('I have disconnected by your order')
        else:
                await ctx.send('I am not connected already!')






client.run('ODc4MTAwNzQzNTE5ODY2ODgw.YR8RCw.EG6iBKqs2cejp1tFwFGHq4YbGkU')