import discord
from discord import Interaction, app_commands, ui
from discord.ext import commands

from bot.bot import WarnetBot
from bot.cogs.ext.tcg.utils import send_missing_permission_error_embed

import datetime, time
from typing import Optional, Literal


class Admin(commands.GroupCog, group_name="admin"):
    
    def __init__(self, bot: WarnetBot) -> None:
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} command(s) {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @commands.guild_only()
    @app_commands.command(name='give-role-on-vc', description='Give a role to all members in a voice channel.')
    @app_commands.describe(vc='Voice channel target.', role='Role that will be given to all members in voice channel target.')
    async def give_role_on_vc(self, interaction: Interaction, vc: discord.VoiceChannel, role: discord.Role) -> None:
        await interaction.response.defer()

        if interaction.user.guild_permissions.administrator:
            cnt = 0
            for member in vc.members:
                if member.get_role(role.id) is None:
                    await member.add_roles(role)
                    cnt += 1

            embed = discord.Embed(
                color=discord.Color.green(),
                title='??? Role successfully given',
                description=f"Role {role.mention} telah diberikan kepada **{cnt}** member di voice channel {vc.mention}.",
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(
                text=f'Given by {str(interaction.user)}',
                icon_url=interaction.user.display_avatar.url
            )
            await interaction.followup.send(embed=embed)

        else:
            await send_missing_permission_error_embed(interaction)

async def setup(bot: WarnetBot) -> None:
    await bot.add_cog(Admin(bot))