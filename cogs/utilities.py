import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import database as db
from config import EMBED_COLOR, ERROR_COLOR, SUCCESS_COLOR, WARNING_COLOR
import asyncio


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now(timezone.utc)

    @commands.hybrid_command(name="ping", description="عرض سرعة الاستجابة للبوت")
    async def ping(self, ctx):
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"سرعة الاستجابة: `{round(self.bot.latency * 1000)}ms`",
            color=EMBED_COLOR
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="uptime", description="عرض وقت تشغيل البوت")
    async def uptime(self, ctx):
        delta = datetime.utcnow() - self.start_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        embed = discord.Embed(
            title="⏱️ وقت التشغيل",
            description=f"`{days}d {hours}h {minutes}m {seconds}s`",
            color=EMBED_COLOR
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="userinfo", description="عرض معلومات المستخدم")
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        roles = [role.mention for role in member.roles[1:]]
        embed = discord.Embed(
            title=f"👤 معلومات {member.display_name}",
            color=member.color or EMBED_COLOR
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="🏷️ الاسم", value=f"{member}", inline=True)
        embed.add_field(name="🆔 المعرف", value=f"`{member.id}`", inline=True)
        embed.add_field(name="📅 تاريخ الإنشاء", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="📥 تاريخ الانضمام", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)
        embed.add_field(name=f"🎭 الأدوار ({len(roles)})", value=" ".join(roles) if roles else "لا يوجد", inline=False)
        embed.set_footer(text=f"طلب بواسطة {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="serverinfo", description="عرض معلومات السيرفر")
    async def serverinfo(self, ctx):
        guild = ctx.guild
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        total_members = guild.member_count
        bots = sum(1 for m in guild.members if m.bot)
        humans = total_members - bots
        boosts = guild.premium_subscription_count
        embed = discord.Embed(
            title=f"📊 معلومات {guild.name}",
            color=EMBED_COLOR
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="👑 المالك", value=f"{guild.owner.mention}" if guild.owner else "غير معروف", inline=True)
        embed.add_field(name="🆔 المعرف", value=f"`{guild.id}`", inline=True)
        embed.add_field(name="📅 تاريخ الإنشاء", value=f"<t:{int(guild.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="👥 الأعضاء", value=f"`{humans}` بشري / `{bots}` بوت", inline=True)
        embed.add_field(name="💬 القنوات", value=f"`{text_channels}` نصية / `{voice_channels}` صوتية", inline=True)
        embed.add_field(name="🎭 الأدوار", value=f"`{len(guild.roles)}`", inline=True)
        embed.add_field(name="🚀 الترقيات", value=f"`{boosts}`", inline=True)
        embed.set_footer(text=f"طلب بواسطة {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="avatar", description="عرض صورة البروفايل")
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(
            title=f"🖼️ صورة {member.display_name}",
            color=member.color or EMBED_COLOR
        )
        embed.set_image(url=member.display_avatar.url)
        embed.add_field(
            name="روابط التحميل",
            value=f"[PNG]({member.display_avatar.with_format('png').url}) | "
                  f"[JPEG]({member.display_avatar.with_format('jpeg').url}) | "
                  f"[WEBP]({member.display_avatar.with_format('webp').url})",
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="roleinfo", description="عرض معلومات الرول")
    async def roleinfo(self, ctx, role: discord.Role):
        permissions = [perm[0].replace("_", " ").title() for perm in role.permissions if perm[1]]
        embed = discord.Embed(
            title=f"🎭 معلومات الرول: {role.name}",
            color=role.color or EMBED_COLOR
        )
        embed.add_field(name="🎨 اللون", value=f"`{role.color}`", inline=True)
        embed.add_field(name="🆔 المعرف", value=f"`{role.id}`", inline=True)
        embed.add_field(name="👥 عدد الأعضاء", value=f"`{len(role.members)}`", inline=True)
        embed.add_field(name="📍 الموضع", value=f"`{role.position}`", inline=True)
        embed.add_field(name="🔒 مرفوعة", value=f"`{'نعم' if role.hoist else 'لا'}`", inline=True)
        embed.add_field(name="🤖 بوت", value=f"`{'نعم' if role.is_bot_managed() else 'لا'}`", inline=True)
        embed.add_field(name="🔗 تلقائية", value=f"`{'نعم' if role.is_default() else 'لا'}`", inline=True)
        embed.add_field(name="⬆️ قابلة للترقية", value=f"`{'نعم' if role.is_mentionable() else 'لا'}`", inline=True)
        if permissions:
            embed.add_field(name="📋 الصلاحيات", value="`, `".join(permissions[:20]) + ("..." if len(permissions) > 20 else ""), inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="afk", description="تعيين حالة AFK")
    async def afk(self, ctx, *, reason: str = "AFK"):
        await db.set_afk(ctx.guild.id, ctx.author.id, reason)
        embed = discord.Embed(
            title="💤 تم تعيين حالة AFK",
            description=f"**{ctx.author.display_name}** أصبح الآن AFK\nالسبب: `{reason}`",
            color=WARNING_COLOR
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="invite", description="رابط دعوة البوت")
    async def invite(self, ctx):
        embed = discord.Embed(
            title="📨 رابط الدعوة",
            description=f"[اضغط هنا لدعوة البوت]({discord.utils.oauth_url(self.bot.user, permissions=discord.Permissions.all())})",
            color=SUCCESS_COLOR
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="poll", description="إنشاء استطلاع (اكتب السؤال ثم الخيارات مفصولين بـ |)")
    async def poll(self, ctx, question: str, *, options_str: str):
        options = [o.strip() for o in options_str.split("|")]
        if len(options) < 2:
            await ctx.send(embed=discord.Embed(description="⚠️ تحتاج إلى خيارين على الأقل مفصولين بـ `|`\nمثال: `!poll أفضل لغة؟ Python | JavaScript | Java`", color=ERROR_COLOR))
            return
        if len(options) > 10:
            await ctx.send(embed=discord.Embed(description="⚠️ لا يمكن أن يكون هناك أكثر من 10 خيارات!", color=ERROR_COLOR))
            return
        number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        description = ""
        for i, option in enumerate(options):
            description += f"{number_emojis[i]} {option}\n"
        embed = discord.Embed(
            title=f"📊 {question}",
            description=description,
            color=EMBED_COLOR
        )
        embed.set_footer(text=f"استطلاع بواسطة {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        message = await ctx.send(embed=embed)
        for i in range(len(options)):
            await message.add_reaction(number_emojis[i])

    @commands.hybrid_command(name="remind", description="تعيين تذكير (صيغة الوقت: 10m, 1h, 1d)")
    async def remind(self, ctx, time: str, *, message: str):
        time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        unit = time[-1].lower()
        if unit not in time_dict:
            await ctx.send(embed=discord.Embed(description="⚠️ صيغة الوقت غير صحيحة! استخدم: `s` للثوانٍ, `m` للدقائق, `h` للساعات, `d` للأيام", color=ERROR_COLOR))
            return
        try:
            amount = int(time[:-1])
        except ValueError:
            await ctx.send(embed=discord.Embed(description="⚠️ رقم الوقت غير صحيح!", color=ERROR_COLOR))
            return
        seconds = amount * time_dict[unit]
        if seconds > 604800:
            await ctx.send(embed=discord.Embed(description="⚠️ الحد الأقصى هو 7 أيام!", color=ERROR_COLOR))
            return
        embed = discord.Embed(
            title="✅ تم تعيين التذكير",
            description=f"سأتذكرك بعد `{time}`:\n{message}",
            color=SUCCESS_COLOR
        )
        await ctx.send(embed=embed)
        await asyncio.sleep(seconds)
        remind_embed = discord.Embed(
            title="🔔 تذكير!",
            description=message,
            color=EMBED_COLOR
        )
        await ctx.send(content=ctx.author.mention, embed=remind_embed)

    @commands.hybrid_command(name="members", description="عرض عدد الأعضاء والبوتات")
    async def members(self, ctx):
        total = ctx.guild.member_count
        bots = sum(1 for m in ctx.guild.members if m.bot)
        humans = total - bots
        embed = discord.Embed(
            title="👥 عدد الأعضاء",
            color=EMBED_COLOR
        )
        embed.add_field(name="الإجمالي", value=f"`{total}`", inline=True)
        embed.add_field(name="البشر", value=f"`{humans}`", inline=True)
        embed.add_field(name="البوتات", value=f"`{bots}`", inline=True)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.guild is None:
            return
        afk_data = await db.get_afk(message.guild.id, message.author.id)
        if afk_data:
            await db.remove_afk(message.guild.id, message.author.id)
            since = datetime.now(timezone.utc) - datetime.fromisoformat(afk_data["since"])
            minutes = int(since.total_seconds() // 60)
            embed = discord.Embed(
                title="👋 مرحباً بعودتك!",
                description=f"لقد كنت AFK لمدة `{minutes}` دقيقة",
                color=SUCCESS_COLOR
            )
            await message.channel.send(embed=embed, delete_after=10)
        for user in message.mentions:
            if user.id == message.author.id:
                continue
            if user.bot:
                continue
            afk_data = await db.get_afk(message.guild.id, user.id)
            if afk_data:
                since = datetime.now(timezone.utc) - datetime.fromisoformat(afk_data["since"])
                minutes = int(since.total_seconds() // 60)
                embed = discord.Embed(
                    title="💤 هذا المستخدم AFK",
                    description=f"**{user.display_name}** حالياً AFK\nالسبب: `{afk_data['reason']}`\nمنذ: `{minutes}` دقيقة",
                    color=WARNING_COLOR
                )
                await message.channel.send(embed=embed, delete_after=10)


async def setup(bot):
    await bot.add_cog(Utilities(bot))
