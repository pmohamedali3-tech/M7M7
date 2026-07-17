import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
import database as db
from config import EMBED_COLOR, ERROR_COLOR, SUCCESS_COLOR, WARNING_COLOR


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def log_embed(self, title, description, color=EMBED_COLOR):
        return discord.Embed(title=title, description=description, color=color)

    async def send_log(self, guild, embed):
        settings = await db.get_logging(guild.id)
        if settings and settings["channel_id"]:
            channel = guild.get_channel(settings["channel_id"])
            if channel:
                await channel.send(embed=embed)

    @commands.hybrid_command(name="kick", description="طرد عضو من السيرفر")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "لا يوجد سبب"):
        if member.top_role >= ctx.author.top_role:
            return await ctx.send(embed=self.log_embed("خطأ", "لا يمكنك طرد عضو بدور أعلى أو مساوي لدورك", ERROR_COLOR))
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send(embed=self.log_embed("خطأ", "لا أستطيع طرد هذا العضو - دوره أعلى من دوري", ERROR_COLOR))

        await member.kick(reason=reason)
        embed = self.log_embed("تم الطرد", f"**{member}** تم طرده من السيرفر\n**السبب:** {reason}\n**بواسطة:** {ctx.author}", WARNING_COLOR)
        await ctx.send(embed=embed)
        await self.send_log(ctx.guild, self.log_embed("👢 طرد", f"**{member}** (ID: {member.id})\n**بواسطة:** {ctx.author}\n**السبب:** {reason}", WARNING_COLOR))

    @commands.hybrid_command(name="ban", description="حظر عضو من السيرفر")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, delete_days: int = 0, *, reason: str = "لا يوجد سبب"):
        if member.top_role >= ctx.author.top_role:
            return await ctx.send(embed=self.log_embed("خطأ", "لا يمكنك حظر عضو بدور أعلى أو مساوي لدورك", ERROR_COLOR))
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send(embed=self.log_embed("خطأ", "لا أستطيع حظر هذا العضو - دوره أعلى من دوري", ERROR_COLOR))

        await member.ban(delete_message_days=delete_days, reason=reason)
        embed = self.log_embed("تم الحظر", f"**{member}** تم حظره من السيرفر\n**السبب:** {reason}\n**بواسطة:** {ctx.author}", ERROR_COLOR)
        await ctx.send(embed=embed)
        await self.send_log(ctx.guild, self.log_embed("🔨 حظر", f"**{member}** (ID: {member.id})\n**بواسطة:** {ctx.author}\n**السبب:** {reason}", ERROR_COLOR))

    @commands.hybrid_command(name="unban", description="إلغاء حظر عضو")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member_id: int):
        try:
            user = await self.bot.fetch_user(member_id)
            await ctx.guild.unban(user)
            embed = self.log_embed("تم إلغاء الحظر", f"**{user}** تم إلغاء حظره", SUCCESS_COLOR)
            await ctx.send(embed=embed)
        except discord.NotFound:
            await ctx.send(embed=self.log_embed("خطأ", "لم يتم العثور على هذا العضو محظور", ERROR_COLOR))

    @commands.hybrid_command(name="mute", description="كتم عضو")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, minutes: int = 10, *, reason: str = "لا يوجد سبب"):
        if member.top_role >= ctx.author.top_role:
            return await ctx.send(embed=self.log_embed("خطأ", "لا يمكنك كتم عضو بدور أعلى أو مساوي لدورك", ERROR_COLOR))

        duration = timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        await db.add_mute(ctx.guild.id, member.id, ctx.author.id, None)

        embed = self.log_embed("تم الكتم", f"**{member}** تم كتمه لمدة **{minutes}** دقيقة\n**السبب:** {reason}\n**بواسطة:** {ctx.author}", WARNING_COLOR)
        await ctx.send(embed=embed)
        await self.send_log(ctx.guild, self.log_embed("🔇 كتم", f"**{member}** (ID: {member.id})\n**المدة:** {minutes} دقيقة\n**بواسطة:** {ctx.author}\n**السبب:** {reason}", WARNING_COLOR))

    @commands.hybrid_command(name="unmute", description="إلغاء كتم عضو")
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        await member.timeout(None)
        await db.remove_mute(ctx.guild.id, member.id)
        embed = self.log_embed("تم إلغاء الكتم", f"**{member}** تم إلغاء كتمه", SUCCESS_COLOR)
        await ctx.send(embed=embed)
        await self.send_log(ctx.guild, self.log_embed("🔊 إلغاء كتم", f"**{member}** (ID: {member.id})\n**بواسطة:** {ctx.author}", SUCCESS_COLOR))

    @commands.hybrid_command(name="warn", description="إنذار عضو")
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "لا يوجد سبب"):
        if member.top_role >= ctx.author.top_role:
            return await ctx.send(embed=self.log_embed("خطأ", "لا يمكنك إنذار عضو بدور أعلى أو مساوي لدورك", ERROR_COLOR))

        count = await db.add_warning(ctx.guild.id, member.id, ctx.author.id, reason)
        embed = self.log_embed("تم الإنذار", f"**{member}** تم إنذاره\n**السبب:** {reason}\n**عدد الإنذارات:** {count}\n**بواسطة:** {ctx.author}", WARNING_COLOR)
        await ctx.send(embed=embed)
        await self.send_log(ctx.guild, self.log_embed("⚠️ إنذار", f"**{member}** (ID: {member.id})\n**بواسطة:** {ctx.author}\n**السبب:** {reason}\n**الإنذارات:** {count}", WARNING_COLOR))

        if count >= 3:
            try:
                await member.ban(reason=f"3 إنذارات - تلقائي")
                await ctx.send(embed=self.log_embed("تم الحظر تلقائياً", f"**{member}** تم حظره تلقائياً بسبب 3 إنذارات", ERROR_COLOR))
            except:
                pass

    @commands.hybrid_command(name="warnings", description="عرض إنذارات عضو")
    @commands.has_permissions(moderate_members=True)
    async def warnings(self, ctx, member: discord.Member):
        warns = await db.get_warnings(ctx.guild.id, member.id)
        if not warns:
            return await ctx.send(embed=self.log_embed("الإنذارات", f"**{member}** ليس لديه أي إنذارات", SUCCESS_COLOR))

        embed = self.log_embed(f"إنذارات {member}", f"**عدد الإنذارات:** {len(warns)}", WARNING_COLOR)
        for w in warns[:10]:
            mod = ctx.guild.get_member(w["moderator_id"])
            mod_name = str(mod) if mod else "Unknown"
            embed.add_field(
                name=f"#{w['id']} - {w['created_at'][:10]}",
                value=f"**السبب:** {w['reason']}\n**بواسطة:** {mod_name}",
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="clearwarnings", description="مسح إنذارات عضو")
    @commands.has_permissions(administrator=True)
    async def clearwarnings(self, ctx, member: discord.Member):
        await db.clear_warnings(ctx.guild.id, member.id)
        embed = self.log_embed("تم مسح الإنذارات", f"تم مسح جميع إنذارات **{member}**", SUCCESS_COLOR)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="purge", description="مسح رسائل")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int = 10):
        if amount > 100:
            return await ctx.send(embed=self.log_embed("خطأ", "لا يمكن مسح أكثر من 100 رسالة", ERROR_COLOR))

        deleted = await ctx.channel.purge(limit=amount + 1)
        embed = self.log_embed("تم المسح", f"تم مسح **{len(deleted) - 1}** رسالة", SUCCESS_COLOR)
        msg = await ctx.send(embed=embed)
        await msg.delete(delay=3)

    @commands.hybrid_command(name="slowmode", description="تفعيل وضع البطيء")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 0):
        await ctx.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await ctx.send(embed=self.log_embed("تم التعطيل", "تم إلغاء وضع البطيء", SUCCESS_COLOR))
        else:
            await ctx.send(embed=self.log_embed("تم التفعيل", f"وضع البطيء: **{seconds}** ثانية", SUCCESS_COLOR))

    @commands.hybrid_command(name="nick", description="تغيير لقب عضو")
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member, *, nickname: str = None):
        await member.edit(nick=nickname)
        if nickname:
            await ctx.send(embed=self.log_embed("تم تغيير اللقب", f"لقـب **{member}** تم تغييره إلى **{nickname}**", SUCCESS_COLOR))
        else:
            await ctx.send(embed=self.log_embed("تم تغيير اللقب", f"لقـب **{member}** تم إعادته للأساسي", SUCCESS_COLOR))

    @commands.hybrid_command(name="lock", description="قفل روم")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        embed = self.log_embed("تم القفل", f"**{channel.mention}** تم قفله", WARNING_COLOR)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="unlock", description="فتح روم")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        embed = self.log_embed("تم الفتح", f"**{channel.mention}** تم فتحه", SUCCESS_COLOR)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="timeout", description=" timeout لعضو")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, hours: int = 0, minutes: int = 0, seconds: int = 0, *, reason: str = "لا يوجد سبب"):
        total_seconds = hours * 3600 + minutes * 60 + seconds
        if total_seconds <= 0:
            return await ctx.send(embed=self.log_embed("خطأ", "حدد مدة صحيحة", ERROR_COLOR))

        duration = timedelta(seconds=total_seconds)
        await member.timeout(duration, reason=reason)
        embed = self.log_embed("تم الإيقاف", f"**{member}** تم إيقافه لمدة **{hours}س {minutes}د {seconds}ث**\n**السبب:** {reason}", WARNING_COLOR)
        await ctx.send(embed=embed)

    @kick.error
    @ban.error
    @unban.error
    @mute.error
    @unmute.error
    @warn.error
    @warnings.error
    @clearwarnings.error
    @purge.error
    @slowmode.error
    @lock.error
    @unlock.error
    @timeout.error
    async def mod_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=self.log_embed("خطأ", "ليس لديك صلاحية لتنفيذ هذا الأمر", ERROR_COLOR))
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(embed=self.log_embed("خطأ", "البوت ليس لديه صلاحية كافية", ERROR_COLOR))
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(embed=self.log_embed("خطأ", "لم يتم العثور على هذا العضو", ERROR_COLOR))
        else:
            await ctx.send(embed=self.log_embed("خطأ", f"حدث خطأ: {str(error)}", ERROR_COLOR))


async def setup(bot):
    await bot.add_cog(Moderation(bot))
