import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import sys
from datetime import datetime, timezone
from config import BOT_TOKEN, PREFIX, BOT_STATUS, EMBED_COLOR, ERROR_COLOR, SUCCESS_COLOR
from database import init_db

intents = discord.Intents.all()
intents.message_content = True
intents.members = True


class ProBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=PREFIX,
            intents=intents,
            help_command=commands.DefaultHelpCommand(
                no_category="الرئيسية",
                width=80
            )
        )
        self.start_time = datetime.now(timezone.utc)

    async def setup_hook(self):
        await init_db()
        cogs_dir = os.path.join(os.path.dirname(__file__), "cogs")
        for filename in os.listdir(cogs_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                cog_name = filename[:-3]
                try:
                    await self.load_extension(f"cogs.{cog_name}")
                    print(f"[OK] Loaded: {cog_name}")
                except Exception as e:
                    print(f"[ERROR] Failed to load {cog_name}: {e}")

        print(f"[OK] Synced slash commands")

    async def on_ready(self):
        await self.tree.sync()
        print(f"{'='*50}")
        print(f"  ProBot is Online!")
        print(f"  Bot: {self.user}")
        print(f"  ID: {self.user.id}")
        print(f"  Servers: {len(self.guilds)}")
        print(f"  Users: {len(self.users)}")
        print(f"  Prefix: {PREFIX}")
        print(f"{'='*50}")
        await self.change_presence(
            activity=discord.Game(name=BOT_STATUS)
        )

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="خطأ",
                description=f"**البرامتر المطلوب:** `{error.param.name}`\n**الاستخدام:** `{ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}`",
                color=ERROR_COLOR
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="خطأ",
                description="**ليس لديك الصلاحية الكافية لتنفيذ هذا الأمر**",
                color=ERROR_COLOR
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                title="خطأ",
                description="**البوت ليس لديه الصلاحية الكافية**",
                color=ERROR_COLOR
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="خطأ",
                description=f"**هذا الأمر فيCooldown**\nجرّب بعد `{error.retry_after:.1f}` ثانية",
                color=ERROR_COLOR
            )
            await ctx.send(embed=embed)
        else:
            print(f"[ERROR] {ctx.command}: {error}")

    async def on_guild_join(self, guild):
        embed = discord.Embed(
            title="شكراً لإضافتي! 🎉",
            description=f"مرحباً! أنا **ProBot** وسأساعدك في إدارة سيرفر **{guild.name}**!\n\n**للبدء:**\n- `{PREFIX}help` - عرض جميع الأوامر\n- `{PREFIX}setwelcome` - ضبط رسالة الترحيب\n- `{PREFIX}setlog` - ضبط روم اللوق",
            color=EMBED_COLOR
        )
        if guild.system_channel:
            try:
                await guild.system_channel.send(embed=embed)
            except:
                pass


bot = ProBot()


@bot.command(name="reload", hidden=True)
@commands.is_owner()
async def reload_cog(ctx, cog_name: str):
    try:
        await bot.reload_extension(f"cogs.{cog_name}")
        await ctx.send(embed=discord.Embed(title="تم", description=f"**{cog_name}** تم إعادة تحميله", color=SUCCESS_COLOR))
    except Exception as e:
        await ctx.send(embed=discord.Embed(title="خطأ", description=str(e), color=ERROR_COLOR))


@bot.command(name="load", hidden=True)
@commands.is_owner()
async def load_cog(ctx, cog_name: str):
    try:
        await bot.load_extension(f"cogs.{cog_name}")
        await ctx.send(embed=discord.Embed(title="تم", description=f"**{cog_name}** تم تحميله", color=SUCCESS_COLOR))
    except Exception as e:
        await ctx.send(embed=discord.Embed(title="خطأ", description=str(e), color=ERROR_COLOR))


@bot.command(name="unload", hidden=True)
@commands.is_owner()
async def unload_cog(ctx, cog_name: str):
    try:
        await bot.unload_extension(f"cogs.{cog_name}")
        await ctx.send(embed=discord.Embed(title="تم", description=f"**{cog_name}** تم إزالته", color=SUCCESS_COLOR))
    except Exception as e:
        await ctx.send(embed=discord.Embed(title="خطأ", description=str(e), color=ERROR_COLOR))


@bot.command(name="servers", hidden=True)
@commands.is_owner()
async def servers_list(ctx):
    guilds = bot.guilds
    embed = discord.Embed(title=f"السيرفرات ({len(guilds)})", color=EMBED_COLOR)
    for g in guilds[:25]:
        embed.add_field(name=g.name, value=f"ID: {g.id} | Members: {g.member_count}", inline=False)
    await ctx.send(embed=embed)


if __name__ == "__main__":
    if not BOT_TOKEN:
        print("[ERROR] BOT_TOKEN not found! Please create a .env file with your bot token.")
        print("Copy .env.example to .env and fill in your bot token.")
        sys.exit(1)
    bot.run(BOT_TOKEN)
