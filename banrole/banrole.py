from discord.ext import commands
import discord

from redbot.core import RedContext, Config, checks


class BanRole:
    """
    Ban and unban by role
    """

    default_role = {
        "banned_members": []
    }

    def __init__(self):
        self.config = Config.get_conf(self, identifier=59595922, force_registration=True)

    @commands.command()
    @checks.admin_or_permissions(ban_members=True)
    async def banrole(self, ctx: RedContext, *, role: discord.Role):
        """
        Ban all members with the specified role

        The bot's role must be higher than the role you want to ban
        """
        failure_list = []
        async with self.config.role(role).banned_members() as banned_list:
            for member in role.members:
                try:
                    await ctx.guild.ban(member)
                except discord.Forbidden:
                    failure_list.append(
                        "{0.name}#{0.discriminator} (id {0.id})".format(
                            member
                        )
                    )
                else:
                    banned_list.append(member.id)
        if failure_list:
            failures = "I failed to ban the following members:\n"
            failures += "\n".join(failure_list)
            await ctx.send(failures)
        else:
            await ctx.tick()

    @commands.command()
    @checks.admin_or_permissions(ban_members=True)
    async def unbanrole(self, ctx: RedContext, *, role: discord.Role):
        """
        Unban members who were banned via banrole and who had the specified role at ban time
        """
        async with self.config.role(role).banned_members() as banned_list:
            for uid in banned_list:
                user = ctx.bot.get_user(uid)
                if user is None:
                    try:
                        user = await ctx.bot.get_user_info(uid)
                    except discord.NotFound:
                        banned_list.remove(uid)
                        return
                try:
                    await ctx.guild.unban(user)
                except discord.Forbidden:
                    pass
                else:
                    banned_list.remove(uid)
        await ctx.tick()
