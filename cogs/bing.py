#command because I am bored lmao
import discord
from discord.ext import commands
from discord.ext.commands import Context


class Bing(commands.Cog, name="bing"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="bing",
        description="Sends Bing Chilling Video",
    )
    async def bing(self, context: Context) -> None:
        """
        Send an MP4 video.

        :param context: The hybrid command context.
        """
        video_url = "https://cdn.discordapp.com/attachments/1262355583437242409/1263475312541307021/videoplayback.mp4?ex=669a5e94&is=66990d14&hm=36536d04fae0547dfd4c0d25e03635028d38dcd1634a1556418425970868f8d4&"
        await context.send(video_url)


async def setup(bot):
    await bot.add_cog(Bing(bot))
