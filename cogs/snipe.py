import discord
from discord.ext import commands
from discord import app_commands

class Snipe(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """
        Initializes the Snipe cog with the bot instance.
        :param bot: The bot instance.
        """
        self.bot = bot
        self.deleted_messages = {}  # Dictionary to store the last deleted message per channel

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """
        Listens for deleted messages and stores them in a dictionary.
        :param message: The message that was deleted.
        """
        self.deleted_messages[message.channel.id] = {
            'author': message.author,
            'content': message.content,
            'timestamp': message.created_at
        }

    @commands.hybrid_command(name='snipe', description='Displays the last deleted message in the channel.')
    async def snipe(self, ctx: commands.Context):
        """
        Command to display the last deleted message in the channel.
        :param ctx: The context of the command.
        """
        # Retrieve the last deleted message from the dictionary
        channel_id = ctx.channel.id
        if channel_id in self.deleted_messages:
            deleted_message = self.deleted_messages[channel_id]
            embed = discord.Embed(
                title="🗑️ Deleted Message",  # Title of the embed
                description=deleted_message['content'],  # Content of the deleted message
                color=0xFF0000  # Red color for the embed
            )
            embed.set_footer(text=f"Author: {deleted_message['author']} | Time: {deleted_message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")  # Footer with author and timestamp
            await ctx.send(embed=embed)  # Send the embed
        else:
            await ctx.send("No messages have been deleted in this channel.")  # Message if no deleted message found

async def setup(bot: commands.Bot):
    """
    Sets up the Snipe cog.
    :param bot: The bot instance.
    """
    await bot.add_cog(Snipe(bot))
