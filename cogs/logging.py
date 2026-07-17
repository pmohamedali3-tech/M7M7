import discord
from discord.ext import commands
import database as db
from config import EMBED_COLOR, ERROR_COLOR, SUCCESS_COLOR, WARNING_COLOR


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="setlog", description="تعيين قناة السجلات")
    @commands.has_permissions(manage_guild=True)
    async def setlog(self, ctx, channel: discord.TextChannel):
        settings = await db.get_logging(ctx.guild.id)
        if not settings:
            await db.set_logging(ctx.guild.id, channel_id=channel.id)
        else:
            await db.set_logging(ctx.guild.id, channel_id=channel.id)

        embed = discord.Embed(
            description=f"تم تعيين قناة السجلات إلى {channel.mention}",
            color=SUCCESS_COLOR
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="logging", description="عرض إعدادات السجلات")
    @commands.has_permissions(manage_guild=True)
    async def logging(self, ctx):
        settings = await db.get_logging(ctx.guild.id)
        if not settings:
            embed = discord.Embed(
                description="لم يتم تعيين قناة سجلات بعد.",
                color=WARNING_COLOR
            )
            return await ctx.send(embed=embed)

        channel = self.bot.get_channel(settings["channel_id"])
        channel_mention = channel.mention if channel else "غير معروف"

        types = {
            "msg_edit": "تعديل الرسائل",
            "msg_delete": "حذف الرسائل",
            "member_join": "انضمام الأعضاء",
            "member_leave": "مغادرة الأعضاء",
            "role_create": "إنشاء الأدوار",
            "role_delete": "حذف الأدوار",
            "channel_create": "إنشاء القنوات",
            "channel_delete": "حذف القنوات",
            "voice_update": "تحديثات الصوت",
            "mod_actions": "إجراءات التنظيم"
        }

        status_enabled = "✅"
        status_disabled = "❌"

        description = f"**قناة السجلات:** {channel_mention}\n\n"
        for key, label in types.items():
            status = status_enabled if settings.get(key) else status_disabled
            description += f"{status} **{label}**\n"

        embed = discord.Embed(
            title="إعدادات السجلات",
            description=description,
            color=EMBED_COLOR
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="togglelog", description="تفعيل أو تعطيل نوع معين من السجلات")
    @commands.has_permissions(manage_guild=True)
    async def togglelog(self, ctx, log_type: str):
        valid_types = [
            "msg_edit", "msg_delete", "member_join", "member_leave",
            "role_create", "role_delete", "channel_create", "channel_delete",
            "voice_update", "mod_actions"
        ]

        if log_type not in valid_types:
            embed = discord.Embed(
                description=f"نوع غير صحيح. الأنواع المتاحة: {', '.join(valid_types)}",
                color=ERROR_COLOR
            )
            return await ctx.send(embed=embed)

        settings = await db.get_logging(ctx.guild.id)
        if not settings:
            await db.set_logging(ctx.guild.id, **{log_type: 1})
            new_state = 1
        else:
            current = settings.get(log_type, 0)
            new_state = 0 if current else 1
            await db.set_logging(ctx.guild.id, **{log_type: new_state})

        state_text = "تم التفعيل ✅" if new_state else "تم التعطيل ❌"
        embed = discord.Embed(
            description=f"**{log_type}**: {state_text}",
            color=SUCCESS_COLOR
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        if before.content == after.content:
            return

        settings = await db.get_logging(before.guild.id)
        if not settings or not settings.get("msg_edit"):
            return

        channel = self.bot.get_channel(settings["channel_id"])
        if not channel:
            return

        embed = discord.Embed(
            title="📝 تعديل رسالة",
            color=EMBED_COLOR
        )
        embed.add_author(name=str(before.author), icon_url=before.author.display_avatar.url)
        embed.add_field(name="القناة", value=before.channel.mention, inline=True)
        embed.add_field(name="الرسالة", value=f"[انتقل للرسالة]({before.jump_url})", inline=True)

        if before.content:
            embed.add_field(name="قبل", value=before.content[:1024] or "فارغ", inline=False)
        if after.content:
            embed.add_field(name="بعد", value=after.content[:1024] or "فارغ", inline=False)

        embed.timestamp = discord.utils.utcnow()
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        settings = await db.get_logging(message.guild.id)
        if not settings or not settings.get("msg_delete"):
            return

        channel = self.bot.get_channel(settings["channel_id"])
        if not channel:
            return

        embed = discord.Embed(
            title="🗑️ حذف رسالة",
            color=EMBED_COLOR
        )
        embed.add_author(name=str(message.author), icon_url=message.author.display_avatar.url)
        embed.add_field(name="القناة", value=message.channel.mention, inline=True)

        if message.content:
            embed.add_field(name="الرسالة", value=message.content[:1024] or "فارغ", inline=False)

        if message.attachments:
            attachments = "\n".join([a.url for a in message.attachments[:5]])
            embed.add_field(name="المرفقات", value=attachments, inline=False)

        embed.timestamp = discord.utils.utcnow()
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        settings = await db.get_logging(member.guild.id)
        if not settings or not settings.get("member_join"):
            return

        channel = self.bot.get_channel(settings["channel_id"])
        if not channel:
            return

        embed = discord.Embed(
            title="➡️ انضمام عضو",
            description=f"{member.mention} انضم إلى السيرفر",
            color=EMBED_COLOR
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="المعرف", value=str(member), inline=True)
        embed.add_field(name="الحساب أُنشأ", value=discord.utils.format_dt(member.created_at, "R"), inline=True)
        embed.add_field(name="عدد الأعضاء", value=member.guild.member_count, inline=True)
        embed.timestamp = discord.utils.utcnow()
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        settings = await db.get_logging(member.guild.id)
        if not settings or not settings.get("member_leave"):
            return

        channel = self.bot.get_channel(settings["channel_id"])
        if not channel:
            return

        embed = discord.Embed(
            title="⬅️ مغادرة عضو",
            description=f"{member.name} غادر السيرفر",
            color=EMBED_COLOR
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="المعرف", value=str(member), inline=True)
        embed.add_field(name="الأدوار", value=", ".join([r.mention for r in member.roles[1:]][:10]) or "لا يوجد", inline=False)
        embed.timestamp = discord.utils.utcnow()
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        settings = await db.get_logging(member.guild.id)
        if not settings or not settings.get("voice_update"):
            return

        channel = self.bot.get_channel(settings["channel_id"])
        if not channel:
            return

        embed = discord.Embed(color=EMBED_COLOR)

        if before.channel is None and after.channel is not None:
            embed.title = "🔊 انضمام لقناة صوتية"
            embed.description = f"{member.mention} انضم إلى {after.channel.mention}"
        elif before.channel is not None and after.channel is None:
            embed.title = "🔇 مغادرة قناة صوتية"
            embed.description = f"{member.name} غادر {before.channel.name}"
        elif before.channel != after.channel:
            embed.title = "🔄 انتقال بين القنوات"
            embed.description = f"{member.name} انتقل من {before.channel.name} إلى {after.channel.mention}"
        else:
            return

        embed.timestamp = discord.utils.utcnow()
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        settings = await db.get_logging(before.guild.id)
        if not settings:
            return

        channel = self.bot.get_channel(settings.get("channel_id"))
        if not channel:
            return

        if before.roles != after.roles:
            added = set(after.roles) - set(before.roles)
            removed = set(before.roles) - set(after.roles)

            if added:
                embed = discord.Embed(
                    title="🏷️ إضافة دور",
                    description=f"{after.mention} حصل على دور {', '.join([r.mention for r in added])}",
                    color=EMBED_COLOR
                )
                embed.timestamp = discord.utils.utcnow()
                await channel.send(embed=embed)

            if removed:
                embed = discord.Embed(
                    title="🏷️ إزالة دور",
                    description=f"{after.mention} فقد دور {', '.join([r.mention for r in removed])}",
                    color=EMBED_COLOR
                )
                embed.timestamp = discord.utils.utcnow()
                await channel.send(embed=embed)

        if before.nick != after.nick:
            embed = discord.Embed(
                title="✏️ تغيير الاسم",
                color=EMBED_COLOR
            )
            embed.add_author(name=str(after), icon_url=after.display_avatar.url)
            embed.add_field(name="الاسم السابق", value=before.nick or "لا يوجد", inline=True)
            embed.add_field(name="الاسم الجديد", value=after.nick or "لا يوجد", inline=True)
            embed.timestamp = discord.utils.utcnow()
            await channel.send(embed=embed)

        if before.timed_out_until != after.timed_out_until:
            if after.timed_out_until:
                embed = discord.Embed(
                    title="🔇 تقييد العضو",
                    description=f"{after.mention} تم تقييده",
                    color=WARNING_COLOR
                )
                embed.add_field(name="المدة", value=discord.utils.format_dt(after.timed_out_until, "R"), inline=True)
            else:
                embed = discord.Embed(
                    title="🔊 إلغاء تقييد العضو",
                    description=f"{after.mention} تم إلغاء تقييده",
                    color=SUCCESS_COLOR
                )
            embed.timestamp = discord.utils.utcnow()
            await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Logging(bot))
