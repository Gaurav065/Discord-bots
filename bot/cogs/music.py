import asyncio
import typing as t
import re
import datetime as dt


import discord
from discord.utils import _URL_REGEX
import wavelink
from discord import player
from discord.ext import commands
from discord.ext.commands import context

URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
OPTIONS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
}


class AlreadyConnectedToChannel(commands.CommandError):
    pass

class NoVoiceChannel(commands.CommandError):
    pass

class QueueIsEmpty(commands.CommandError):
    pass

class NoTrackFound(commands.CommandError):
    pass

class Queue:
    def __init__(self):
        self._queue = []
        self.position = 0

    def add(self, *args):
        self._queue.extend(args)
        
    @property
    def is_empty(self):
        return not self._queue

    @property
    def first_track(self):
        if not self._queue:
            raise QueueIsEmpty

        return self._queue[0]

    def get_next_track(self):
        if not self._queue:
            raise QueueIsEmpty
        
        self.position += 1

        if self.position > len(self._queue)-1:
            return None
        
        return self._queue[self.position]




class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = Queue()

    async def connect(self, ctx, channel=None):
        if self.is_connected:
            raise AlreadyConnectedToChannel

        if(channel:= getattr(ctx.author.voice, "channel", channel)) is None:
            raise NoVoiceChannel

        await super().connect(channel.id)
        return channel

    async def break_cons(self):
        try:
            await self.destroy()
        
        except KeyError:
            pass

    async def add_tracks(self, ctx, tracks):
        if not tracks:
            raise NoTrackFound

        if isinstance(tracks, wavelink.TrackPlaylist):
            self.queue.add(*tracks.tracks)
        elif len(tracks) == 1:
            self.queue.add(tracks[0])
            await ctx.send(f"Ok, I have added {tracks[0].title} to the playlist.")
        else:
            if (track:= await self.choose_track(ctx, tracks)) is not None:
                self.queue.add(track)
                await ctx.send(f"Ok, I have added {track.title} to the playlist.")

        if not self.is_playing and not self.queue.is_empty:
            await self.start_playback()

    async def choose_track(self, ctx, tracks):
        def _check(r,u):
            return (
                r.emoji in OPTIONS.keys()
                and u == ctx.author
                and r.message.id == msg.id
            )
        embed = discord.Embed(
            title="Choose an song",
            description=(
                "\n".join(
                    f"**{i+1}.** {t.title} ({t.length//60000}:{str(t.length%60).zfill(2)})"
                    for i, t in enumerate(tracks[:5])
                )
            ),
            colour=ctx.author.colour,
            timesatamp=dt.datetime.utcnow()
        )
        embed.set_author(name="Search results")
        embed.set_footer(text=f"Invoked by {ctx.author.display_name}", icon_url= ctx.author.avatar_url)
        msg = await ctx.send(embed=embed)
        for emoji in list(OPTIONS.keys())[:min(len(tracks), len(OPTIONS))]:
            await msg.add_reaction(emoji)


        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=_check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.message.delete()
        else:
            await msg.delete()
            return tracks[OPTIONS[reaction.emoji]]




    async def start_playback(self):
        await self.play(self.queue.first_track)

    async def advance(self):
        try:
            if(track:= self.queue.get_next_track()) is not None:
                await self.play(track)
        except QueueIsEmpty:
            pass



class Music(commands.Cog, wavelink.WavelinkMixin):
    def __init__(self, bot):
        self.bot = bot
        self.wavelink = wavelink.Client(bot=bot)
        self.bot.loop.create_task(self.start_nodes())

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                await self.get_player(member.guild)

    
    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node):
        print(f"Wavelink node '{node.identifier}' ready.")


    @wavelink.WavelinkMixin.listener("on_track_stuck")
    @wavelink.WavelinkMixin.listener("on_track_end")
    @wavelink.WavelinkMixin.listener("on_track_exception")    
    async def on_player_stop(self, node, payload):
        await payload.player.advance()


    async def cog_check(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Sorry sir, But music commands are not availaible in direct messages. Thank You for using me, please support my master.")
            return False

        return True

    
    async def start_nodes(self):
        await self.bot.wait_until_ready()

        nodes = {
            "MAIN":{
                "host": "127.0.0.1",
                "port": 2333,
                "rest_uri": "http://127.0.0.1:2333",
                "password": "youshallnotpass",
                "identifier": "MAIN",
                "region": "india",
            }
        }
        for node in nodes.values():
            await self.wavelink.initiate_node(**node)

    def get_player(self, obj):
        if isinstance(obj, commands.Context):
            return self.wavelink.get_player(obj.guild.id, cls=Player, context= obj)
        elif isinstance(obj, discord.Guild):
            return self.wavelink.get_player(obj.id, cls=Player)
    
    @commands.command(__name__="connect", aliases=["join","summon","j"])
    async def connect_com(self, ctx, *, channel:t.Optional[discord.VoiceChannel]):
        player = self.get_player(ctx)
        channel = await player.connect(ctx, channel)
        await ctx.send(f"Connected to the voice channel {channel.name}")


    @connect_com.error
    async def connect_command_error(self, ctx, exc):
        if isinstance(exc, AlreadyConnectedToChannel):
            await ctx.send("Already connected to the voice channel")
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send("Requirements for the voice channel were not met.")
        
    @commands.command(__name__="Disconnect", aliases=["leave","l","break"])
    async def diconnect_com(self, ctx):
        player = self.get_player(ctx)
        await player.break_cons()
        await ctx.send("Disconnected from the voice channel")

    @commands.command(name="play", aliases=["p"])
    async def play_com(self, ctx, *, query: t.Optional[str]):
        player = self.get_player(ctx)

        if not player.is_connected:
            await player.connect(ctx)

        if query is None:
            pass

        else: 
            query = query.strip("<>")
            if not re.match(URL_REGEX, query):
                query = f"ytsearch:{query}"

            await player.add_tracks(ctx, await self.wavelink.get_tracks(query))
            



def setup(bot):
    bot.add_cog(Music(bot))
