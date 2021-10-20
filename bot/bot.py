import pathlib
from pathlib import Path

import discord
from discord.ext import commands


class Mbot(commands.Bot):
    def __init__(self):
        self._cogs = [p.stem for p in Path(".").glob("./bot/cogs/*.py")]
        
        intents = discord.Intents.default()
        intents.members = True
        
        super().__init__(
            command_prefix=self.prefix,
            case_insensitive=True,
            intents=discord.Intents.all()
            )

    def setup(self):
        print("INITIATING... . . . ")

        for cog in self._cogs:
            self.load_extension(f"bot.cogs.{cog}")
            print(f" loaded '{cog}' cog.")

        print("Loading complete")

    def run(self):
        self.setup()

        with open(r"C:\Users\dell\Desktop\Discord bots\Data\token.0", "r", encoding="utf-8") as f:
            TOKEN = f.read()

        print("Starting.., preparing assets, please wait for a moment while the assests are loading it may take nano seconds... ... ")
        super().run(TOKEN, reconnect=True)

    async def shutdown(self):
        print("Unloading all assets and breaking connection with Discord.. ... ... ... .. ")
        await super().close()

    async def close(self):
        print("Awaiting termination command from input device")
        await self.shutdown()

    async def on_connect(self):
        print(f"Respawn successful (ping: {self.latency*1000} ms)")

    async def on_resumed(self):
        print("The hp has been restored, ready for re-deployment")
    
    async def on_disconnect(self):
        print("Lpu_bot remaining hp has been depleted")
    
    # async def on_error(self, err, *args, **kwargs):
    #     raise

    # async def on_command_error(self, ctx, exc):
    #     raise getattr(exc, "Real_one", exc)



    async def on_ready(self):
        self.client_id = (await self.application_info()).id
        print("Bot is ready for deployment")

    async def prefix(self, bot , msg):
        return commands.when_mentioned_or(".")(bot, msg)

    async def commands_process(self, msg):
        ctx = await self.get_context(msg, cls=commands.Context)

        if ctx.command is not None:
            await self.invoke(ctx)
    
    async def on_message(self,msg):
        if not msg.author.bot:
            await self.process_commands(msg)
