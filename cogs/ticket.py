import discord
from discord.ext import commands
from discord.ui import Button, View
from discord import Embed, Colour, Interaction

class Ticket(commands.Cog):
    def __init__(self, bot):
        """
        Initializes the Ticket cog with the bot instance.
        :param bot: The bot instance.
        """
        self.bot = bot

    @commands.hybrid_command(name="testticket", description="Create a ticket")
    async def testticket(self, ctx):
        """
        Command to create a test ticket with a selection of services.
        :param ctx: The context of the command.
        """
        embed = Embed(
            title="NAME",  # Replace with your bot name or service name
            description="> DESCRIPTION",  # Replace with your service description
            color=Colour.purple()
        )
        embed.set_footer(text="⚠️ Creating tickets for fun is punished by a ban!")
        embed.set_image(url="https://media.discordapp.net/attachments/1262355583437242409/1264335052964102256/9AF43C82-13BC-4CE2-9F48-D536C77AF86C.png?ex=669d7f46&is=669c2dc6&hm=69642441909eaf5f78e444dd5244f834a7ee4390c5c46449b9715ec914d09ddd&=&format=webp&quality=lossless&width=810&height=224")
        
        # Create a view with interactive buttons
        view = TicketView(ctx.author)
        await ctx.send(embed=embed, view=view)

class TicketView(View):
    def __init__(self, user):
        """
        Initializes the TicketView with user information.
        :param user: The user who invoked the ticket command.
        """
        super().__init__(timeout=None)
        self.user = user

    @discord.ui.button(label="Button 1", style=discord.ButtonStyle.gray, custom_id="services", emoji="🛒")
    async def services_button(self, interaction: Interaction, button: Button):
        """
        Button for creating a ticket for paid services.
        :param interaction: The interaction object.
        :param button: The button object.
        """
        await self.create_ticket(interaction, "services")

    @discord.ui.button(label="Button 2", style=discord.ButtonStyle.gray, custom_id="report", emoji="🕵️")
    async def report_button(self, interaction: Interaction, button: Button):
        """
        Button for creating a ticket to report a scam.
        :param interaction: The interaction object.
        :param button: The button object.
        """
        await self.create_ticket(interaction, "report")

    @discord.ui.button(label="Button 3", style=discord.ButtonStyle.gray, custom_id="support", emoji="⚙️")
    async def support_button(self, interaction: Interaction, button: Button):
        """
        Button for creating a support ticket.
        :param interaction: The interaction object.
        :param button: The button object.
        """
        await self.create_ticket(interaction, "support")

    async def create_ticket(self, interaction, type_):
        """
        Creates a new ticket channel based on the type of request.
        :param interaction: The interaction object.
        :param type_: The type of ticket to create (services, report, support).
        """
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="Tickets")  # Ensure this category exists

        existing_channel = discord.utils.get(guild.text_channels, name=f"{type_}-{self.user.name}")
        if existing_channel:
            await interaction.response.send_message(f"You already have a ticket: {existing_channel.mention}", ephemeral=True)
        else:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                self.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            channel = await guild.create_text_channel(f"{type_}-{self.user.name}", category=category, overwrites=overwrites)
            
            # Customize embed content based on ticket type
            if type_ == "services":
                embed = Embed(
                    title="Paid Services",
                    color=Colour.purple()
                )
                embed.add_field(name="Thank you for creating an order, someone will start attending to you soon!", value="Please describe what service you are interested in. If you have any questions, feel free to ask!\n\nPlease wait patiently for a response!", inline=False)
                embed.add_field(name="Our Services:", value="\n".join([
                    "text"
                ]), inline=False)
                embed.set_thumbnail(url="https://gymporn.cz/files/hqdefault.jpg")  # Change URL if necessary
                view = CloseClaimView()
                await channel.send(embed=embed, view=view)
            else:
                await channel.send(embed=Embed(title="Ticket Created", description=f"Ticket: {channel.mention}", color=Colour.green()))
            
            await interaction.response.send_message(f"Ticket created: {channel.mention}", ephemeral=True)

class CloseClaimView(View):
    def __init__(self):
        """
        Initializes the CloseClaimView with interactive buttons for managing tickets.
        """
        super().__init__(timeout=None)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, custom_id="close", emoji="❌")
    async def close_button(self, interaction: Interaction, button: Button):
        """
        Button to close (delete) the ticket channel.
        :param interaction: The interaction object.
        :param button: The button object.
        """
        await interaction.channel.delete()

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.success, custom_id="claim", emoji="⬇️")
    async def claim_button(self, interaction: Interaction, button: Button):
        """
        Button to claim (acknowledge) the ticket.
        :param interaction: The interaction object.
        :param button: The button object.
        """
        await interaction.response.send_message("Ticket claimed!", ephemeral=True)

async def setup(bot):
    """
    Sets up the Ticket cog.
    :param bot: The bot instance.
    """
    await bot.add_cog(Ticket(bot))
