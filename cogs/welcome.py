import discord
from discord.ext import commands
import database as db
from config import EMBED_COLOR, ERROR_COLOR, SUCCESS_COLOR


def format_message(message: str, member: discord.Member) -> str:
    if not message:
        return message
    return (
        message
        .replace("{user}", member.mention)
        .replace("{server}", member.guild.name)
        .replace("{count}", str(member.guild.member_count))
    )


class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="setwelcome", description="تعيين قناة ورسالة الترحيب")
    @commands.has_permissions(manage_guild=True)
    async def set_welcome(self, ctx: commands.Context, channel: discord.TextChannel, *, message: str = None):
        await db.set_welcome(ctx.guild.id, channel.id, message=message, enabled=True)
        embed = discord.Embed(
            title="تم تعيين الترحيب",
            description=f"تم تعيين قناة الترحيب إلى {channel.mention}",
            color=SUCCESS_COLOR
        )
        if message:
            embed.add_field(name="الرسالة", value=message, inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="setgoodbye", description="تعيين قناة ورسالة الوداع")
    @commands.has_permissions(manage_guild=True)
    async def set_goodbye(self, ctx: commands.Context, channel: discord.TextChannel, *, message: str = None):
        await db.set_goodbye(ctx.guild.id, channel.id, message=message, enabled=True)
        embed = discord.Embed(
            title="تم تعيين الوداع",
            description=f"تم تعيين قناة الوداع إلى {channel.mention}",
            color=SUCCESS_COLOR
        )
        if message:
            embed.add_field(name="الرسالة", value=message, inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="testwelcome", description="اختبار رسالة الترحيب")
    @commands.has_permissions(manage_guild=True)
    async def test_welcome(self, ctx: commands.Context):
        data = await db.get_welcome(ctx.guild.id)
        if not data or not data.get("channel_id"):
            embed = discord.Embed(
                title="خطأ",
                description="لم يتم تعيين قناة الترحيب بعد.",
                color=ERROR_COLOR
            )
            await ctx.send(embed=embed)
            return
        channel = ctx.guild.get_channel(data["channel_id"])
        if not channel:
            embed = discord.Embed(
                title="خطأ",
                description="قناة الترحيب غير موجودة.",
                color=ERROR_COLOR
            )
            await ctx.send(embed=embed)
            return
        msg = data.get("message") or "مرحباً {user} في {server}!"
        formatted = format_message(msg, ctx.author)
        embed = discord.Embed(
            title="اختبار الترحيب",
            description=formatted,
            color=EMBED_COLOR
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="testgoodbye", description="اختبار رسالة الوداع")
    @commands.has_permissions(manage_guild=True)
    async def test_goodbye(self, ctx: commands.Context):
        data = await db.get_goodbye(ctx.guild.id)
        if not data or not data.get("channel_id"):
            embed = discord.Embed(
                title="خطأ",
                description="لم يتم تعيين قناة الوداع بعد.",
                color=ERROR_COLOR
            )
            await ctx.send(embed=embed)
            return
        channel = ctx.guild.get_channel(data["channel_id"])
        if not channel:
            embed = discord.Embed(
                title="خطأ",
                description="قناة الوداع غير موجودة.",
                color=ERROR_COLOR
            )
            await ctx.send(embed=embed)
            return
        msg = data.get("message") or "وداعاً {user}!"
        formatted = format_message(msg, ctx.author)
        embed = discord.Embed(
            title="اختبار الوداع",
            description=formatted,
            color=EMBED_COLOR
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="setautorole", description="تعيين رتبة تلقائية للأعضاء الجدد")
    @commands.has_permissions(manage_guild=True)
    async def set_autorole(self, ctx: commands.Context, role: discord.Role):
        await db.set_autorole(ctx.guild.id, role.id, enabled=True)
        embed = discord.Embed(
            title="تم تعيين الرتبة التلقائية",
            description=f"سيحصل الأعضاء الجدد على رتبة {role.mention} تلقائياً.",
            color=SUCCESS_COLOR
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="welcomeconfig", description="عرض إعدادات الترحيب")
    @commands.has_permissions(manage_guild=True)
    async def welcome_config(self, ctx: commands.Context):
        data = await db.get_welcome(ctx.guild.id)
        if not data or not data.get("channel_id"):
            embed = discord.Embed(
                title="إعدادات الترحيب",
                description="لم يتم تعيين إعدادات الترحيب بعد.",
                color=ERROR_COLOR
            )
            await ctx.send(embed=embed)
            return
        channel = ctx.guild.get_channel(data["channel_id"])
        enabled = data.get("enabled", False)
        status = "مفعّل" if enabled else "معطّل"
        embed = discord.Embed(
            title="إعدادات الترحيب",
            color=EMBED_COLOR
        )
        embed.add_field(name="القناة", value=channel.mention if channel else "غير موجودة", inline=True)
        embed.add_field(name="الحالة", value=status, inline=True)
        msg = data.get("message") or "مرحباً {user} في {server}!"
        embed.add_field(name="الرسالة", value=msg, inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="goodbyeconfig", description="عرض إعدادات الوداع")
    @commands.has_permissions(manage_guild=True)
    async def goodbye_config(self, ctx: commands.Context):
        data = await db.get_goodbye(ctx.guild.id)
        if not data or not data.get("channel_id"):
            embed = discord.Embed(
                title="إعدادات الوداع",
                description="لم يتم تعيين إعدادات الوداع بعد.",
                color=ERROR_COLOR
            )
            await ctx.send(embed=embed)
            return
        channel = ctx.guild.get_channel(data["channel_id"])
        enabled = data.get("enabled", False)
        status = "مفعّل" if enabled else "معطّل"
        embed = discord.Embed(
            title="إعدادات الوداع",
            color=EMBED_COLOR
        )
        embed.add_field(name="القناة", value=channel.mention if channel else "غير موجودة", inline=True)
        embed.add_field(name="الحالة", value=status, inline=True)
        msg = data.get("message") or "وداعاً {user}!"
        embed.add_field(name="الرسالة", value=msg, inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="disablewelcome", description="تعطيل رسالة الترحيب")
    @commands.has_permissions(manage_guild=True)
    async def disable_welcome(self, ctx: commands.Context):
        data = await db.get_welcome(ctx.guild.id)
        if not data or not data.get("channel_id"):
            embed = discord.Embed(
                title="خطأ",
                description="لم يتم تعيين إعدادات الترحيب بعد.",
                color=ERROR_COLOR
            )
            await ctx.send(embed=embed)
            return
        await db.set_welcome(ctx.guild.id, data["channel_id"], enabled=False)
        embed = discord.Embed(
            title="تم تعطيل الترحيب",
            description="تم تعطيل رسائل الترحيب بنجاح.",
            color=SUCCESS_COLOR
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="disablegoodbye", description="تعطيل رسالة الوداع")
    @commands.has_permissions(manage_guild=True)
    async def disable_goodbye(self, ctx: commands.Context):
        data = await db.get_goodbye(ctx.guild.id)
        if not data or not data.get("channel_id"):
            embed = discord.Embed(
                title="خطأ",
                description="لم يتم تعيين إعدادات الوداع بعد.",
                color=ERROR_COLOR
            )
            await ctx.send(embed=embed)
            return
        await db.set_goodbye(ctx.guild.id, data["channel_id"], enabled=False)
        embed = discord.Embed(
            title="تم تعطيل الوداع",
            description="تم تعطيل رسائل الوداع بنجاح.",
            color=SUCCESS_COLOR
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot:
            return
        welcome_data = await db.get_welcome(member.guild.id)
        if welcome_data and welcome_data.get("channel_id") and welcome_data.get("enabled"):
            channel = member.guild.get_channel(welcome_data["channel_id"])
            if channel:
                msg = welcome_data.get("message") or "مرحباً {user} في {server}!"
                formatted = format_message(msg, member)
                embed = discord.Embed(description=formatted, color=EMBED_COLOR)
                embed.set_thumbnail(url=member.display_avatar.url)
                try:
                    await channel.send(embed=embed)
                except discord.Forbidden:
                    pass
        autorole_data = await db.get_autorole(member.guild.id)
        if autorole_data and autorole_data.get("role_id") and autorole_data.get("enabled"):
            role = member.guild.get_role(autorole_data["role_id"])
            if role:
                try:
                    await member.add_roles(role, reason="Auto role on join")
                except discord.Forbidden:
                    pass

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member.bot:
            return
        goodbye_data = await db.get_goodbye(member.guild.id)
        if goodbye_data and goodbye_data.get("channel_id") and goodbye_data.get("enabled"):
            channel = member.guild.get_channel(goodbye_data["channel_id"])
            if channel:
                msg = goodbye_data.get("message") or "وداعاً {user}!"
                formatted = format_message(msg, member)
                embed = discord.Embed(description=formatted, color=EMBED_COLOR)
                embed.set_thumbnail(url=member.display_avatar.url)
                try:
                    await channel.send(embed=embed)
                except discord.Forbidden:
                    pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))
