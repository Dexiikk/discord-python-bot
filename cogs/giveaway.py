import discord, random, asyncio
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta

class Giveaway(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """
        Initializes the Giveaway cog with the bot instance.
        :param bot: The bot instance.
        """
        self.bot = bot
        self.giveaway_message_id = None
        self.giveaway_channel_id = None
        self.giveaway_entrants = []
        self.giveaway_end_time = None

    @commands.hybrid_command(name='startgiveaway', description='Start a giveaway.')
    @commands.has_permissions(administrator=True)
    @app_commands.describe(
        time='Duration of the giveaway in seconds', 
        prize='The prize for the giveaway', 
        winners='Number of winners', 
        description='Description of the giveaway'
    )
    async def start_giveaway(self, ctx: commands.Context, time: int, winners: int, prize: str, *, description: str = "Participate in the giveaway to win a great prize!"):
        """
        Command to start a giveaway.
        :param ctx: The context of the command.
        :param time: Duration of the giveaway in seconds.
        :param winners: Number of winners.
        :param prize: The prize for the giveaway.
        :param description: Description of the giveaway.
        """
        end_time = datetime.utcnow() + timedelta(seconds=time)
        self.giveaway_end_time = end_time

        embed = discord.Embed(
            title="🎉 **GIVEAWAY** 🎉",  # Title of the giveaway embed
            description=description,  # Description of the giveaway
            color=discord.Color.purple()
        )
        embed.add_field(name="Prize", value=prize, inline=False)  # Prize field
        embed.add_field(name="Remaining Time", value=self.get_remaining_time_str(), inline=False)  # Time left for the giveaway
        embed.add_field(name="Host", value=f"{ctx.author.mention}", inline=False)  # Host of the giveaway
        embed.add_field(name="Number of Winners", value=f"{winners}", inline=False)  # Number of winners
        embed.set_footer(text="React with 🎉 to participate!")  # Footer text
        embed.set_image(url="https://media.discordapp.net/attachments/1262355583437242409/1263093254329466880/fagagsdfgsdf.png?ex=6698fac2&is=6697a942&hm=c4a8372739481452038e5976a43efb0a284147fc4493205b4186e52203afc95b&=&format=webp&quality=lossless&width=810&height=222")  # Image for the giveaway embed

        # Send the giveaway message
        await ctx.interaction.response.send_message(embed=embed)
        message = await ctx.interaction.original_response()
        await message.add_reaction("🎉")  # Add a reaction to the message

        # Save giveaway details
        self.giveaway_message_id = message.id
        self.giveaway_channel_id = ctx.channel.id
        self.giveaway_entrants = []

        # Schedule the giveaway to end
        await self.end_giveaway(time, prize, winners, ctx.channel.id, message.id)
        return

    def get_remaining_time_str(self):
        """
        Get the remaining time of the giveaway as a human-readable string.
        :return: The remaining time in a Discord timestamp format or a message if the giveaway has ended.
        """
        if self.giveaway_end_time:
            unix_timestamp = int(self.giveaway_end_time.timestamp())
            return f"<t:{unix_timestamp}:R>"  # Discord timestamp format
        return "Giveaway has ended!"  # Message if giveaway has ended

    async def end_giveaway(self, time: int, prize: str, winners: int, channel_id: int, message_id: int):
        """
        Ends the giveaway after the specified duration, selects winners, and creates channels for them.
        :param time: Duration of the giveaway in seconds.
        :param prize: The prize for the giveaway.
        :param winners: Number of winners.
        :param channel_id: ID of the channel where the giveaway was held.
        :param message_id: ID of the message containing the giveaway.
        """
        await asyncio.sleep(time)  # Wait for the giveaway duration
        channel = self.bot.get_channel(channel_id)
        message = await channel.fetch_message(message_id)

        # Get users who reacted to the giveaway
        reaction = discord.utils.get(message.reactions, emoji="🎉")
        users = [user async for user in reaction.users() if not user.bot]

        if len(users) == 0:
            await channel.send("No participants were registered.")
            return

        winners_list = random.sample(users, k=min(len(users), winners))  # Randomly select winners

        for winner in winners_list:
            # Create a private channel for each winner
            overwrites = {
                channel.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                winner: discord.PermissionOverwrite(read_messages=True)
            }
            new_channel = await channel.guild.create_text_channel(
                name=f"{prize.replace(' ', '-')}-{winner.display_name}",
                overwrites=overwrites
            )

            # Send a message to the winner
            await new_channel.send(f"{winner.mention} you have won the giveaway for {prize}!")

            # Add administrators to the new channel
            for member in channel.guild.members:
                if member.guild_permissions.administrator:
                    await new_channel.set_permissions(member, read_messages=True)

        winners_mentions = "\n".join([winner.mention for winner in winners_list])  # Mention winners

        # Update the giveaway message to show winners
        await message.edit(embed=discord.Embed(
            title="🎉 **GIVEAWAY ENDED** 🎉",
            description=f"WINNERS:\n{winners_mentions}\n\n**PRIZE:** {prize}",
            color=discord.Color.green()
        ))

async def setup(bot: commands.Bot):
    """
    Sets up the Giveaway cog.
    :param bot: The bot instance.
    """
    await bot.add_cog(Giveaway(bot))
