import discord
from discord.ext import commands
import database as db
from config import EMBED_COLOR, ERROR_COLOR, SUCCESS_COLOR


class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="addcommand", description="إضافة أمر مخصص جديد")
    @commands.has_permissions(manage_guild=True)
    async def addcommand(self, ctx: commands.Context, name: str, *, response: str):
        if ctx.guild is None:
            embed = discord.Embed(
                description="لا يمكن استخدام هذا الأمر في الخاص.",
                color=ERROR_COLOR
            )
            return await ctx.send(embed=embed)

        existing = await db.get_custom_command(ctx.guild.id, name)
        if existing:
            embed = discord.Embed(
                description=f"الأمر **{name}** موجود بالفعل.",
                color=ERROR_COLOR
            )
            return await ctx.send(embed=embed)

        await db.set_custom_command(ctx.guild.id, name, response, ctx.author.id)

        embed = discord.Embed(
            title="تم إضافة الأمر",
            description=f"تم إضافة الأمر **{name}** بنجاح.",
            color=SUCCESS_COLOR
        )
        embed.add_field(name="الرد", value=response, inline=False)
        embed.set_footer(text=f"أنشأه {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="delcommand", description="حذف أمر مخصص")
    @commands.has_permissions(manage_guild=True)
    async def delcommand(self, ctx: commands.Context, name: str):
        if ctx.guild is None:
            embed = discord.Embed(
                description="لا يمكن استخدام هذا الأمر في الخاص.",
                color=ERROR_COLOR
            )
            return await ctx.send(embed=embed)

        existing = await db.get_custom_command(ctx.guild.id, name)
        if not existing:
            embed = discord.Embed(
                description=f"الأمر **{name}** غير موجود.",
                color=ERROR_COLOR
            )
            return await ctx.send(embed=embed)

        await db.delete_custom_command(ctx.guild.id, name)

        embed = discord.Embed(
            title="تم حذف الأمر",
            description=f"تم حذف الأمر **{name}** بنجاح.",
            color=SUCCESS_COLOR
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="commands", description="قائمة الأوامر المخصصة")
    async def commands_list(self, ctx: commands.Context):
        if ctx.guild is None:
            embed = discord.Embed(
                description="لا يمكن استخدام هذا الأمر في الخاص.",
                color=ERROR_COLOR
            )
            return await ctx.send(embed=embed)

        all_commands = await db.get_all_custom_commands(ctx.guild.id)

        if not all_commands:
            embed = discord.Embed(
                description="لا توجد أوامر مخصصة في هذا السيرفر.",
                color=ERROR_COLOR
            )
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title="الأوامر المخصصة",
            color=EMBED_COLOR
        )

        for cmd in all_commands:
            creator = ctx.guild.get_member(cmd["created_by"])
            creator_name = creator.display_name if creator else "غير معروف"
            created_at = cmd.get("created_at", "غير معروف")
            embed.add_field(
                name=f"!{cmd['command_name']}",
                value=f"**الرد:** {cmd['response']}\n**أنشأه:** {creator_name}\n**تاريخ الإنشاء:** {created_at}",
                inline=False
            )

        embed.set_footer(text=f"إجمالي الأوامر: {len(all_commands)}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="commandinfo", description="عرض معلومات أمر مخصص")
    async def commandinfo(self, ctx: commands.Context, name: str):
        if ctx.guild is None:
            embed = discord.Embed(
                description="لا يمكن استخدام هذا الأمر في الخاص.",
                color=ERROR_COLOR
            )
            return await ctx.send(embed=embed)

        cmd = await db.get_custom_command(ctx.guild.id, name)
        if not cmd:
            embed = discord.Embed(
                description=f"الأمر **{name}** غير موجود.",
                color=ERROR_COLOR
            )
            return await ctx.send(embed=embed)

        creator = ctx.guild.get_member(cmd["created_by"])
        creator_name = creator.display_name if creator else "غير معروف"
        created_at = cmd.get("created_at", "غير معروف")

        embed = discord.Embed(
            title=f"معلومات الأمر: {name}",
            color=EMBED_COLOR
        )
        embed.add_field(name="الأمر", value=f"!{cmd['command_name']}", inline=True)
        embed.add_field(name="الرد", value=cmd["response"], inline=False)
        embed.add_field(name="أنشأه", value=creator_name, inline=True)
        embed.add_field(name="تاريخ الإنشاء", value=str(created_at), inline=True)
        embed.set_footer(text=f"سيرفر: {ctx.guild.name}")

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.guild is None:
            return
        if not message.content.startswith("!"):
            return

        command_name = message.content.split()[0][1:]
        if not command_name:
            return

        cmd = await db.get_custom_command(message.guild.id, command_name)
        if cmd:
            await message.channel.send(cmd["response"])


async def setup(bot):
    await bot.add_cog(CustomCommands(bot))
