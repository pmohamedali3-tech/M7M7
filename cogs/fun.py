import discord
from discord.ext import commands
import random
import asyncio
from config import EMBED_COLOR, ERROR_COLOR, SUCCESS_COLOR


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="8ball", description="اسأل الكرة السحرية")
    async def eightball(self, ctx, *, question: str):
        responses = [
            "نعم بالتأكيد! 🎱", "لا كلياً 🎱", "ربما 🎱", "لا أستطيع أن أخبر 🎱",
            "اسأل مرة أخرى لاحقاً 🎱", "بالتأكيد نعم! 🎱", "لا أظن ذلك 🎱",
            "من المحتمل 🎱", "شكوكية 🎱", "نعم! 🎱", "لا 🎱",
            "الأرقام تقول نعم 🎱", "اتركها على المجهول 🎱", "نعم لكن كن حذراً 🎱"
        ]
        embed = discord.Embed(title="🎱 الكرة السحرية", color=EMBED_COLOR)
        embed.add_field(name="السؤال", value=question, inline=False)
        embed.add_field(name="الإجابة", value=random.choice(responses), inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="roll", description="ارمي النرد")
    async def roll(self, ctx, sides: int = 6):
        result = random.randint(1, sides)
        embed = discord.Embed(title="🎲 النرد", description=f"**{result}** من أصل **{sides}**", color=EMBED_COLOR)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="flip", description="ارمي العملة")
    async def flip(self, ctx):
        result = random.choice(["🪙Face", "🪙Tails"])
        embed = discord.Embed(title="🪙 العملة", description=f"**{result}**", color=EMBED_COLOR)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="choose", description="اختار من عدة خيارات")
    async def choose(self, ctx, *, choices: str):
        choice_list = [c.strip() for c in choices.split("|")]
        if len(choice_list) < 2:
            return await ctx.send(embed=discord.Embed(title="خطأ", description="اكتب الخيارين مفصولين بـ `|`\nمثال: `pizza | burger | pasta`", color=ERROR_COLOR))
        embed = discord.Embed(title="🤔 أختار...", description=f"**{random.choice(choice_list)}**", color=EMBED_COLOR)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="rps", description="حجر ورقة مقص")
    async def rps(self, ctx, choice: str):
        choices = {"rock": "🪨", "paper": "📄", "scissors": "✂️", "حجر": "🪨", "ورقة": "📄", "مقص": "✂️"}
        choice_lower = choice.lower()
        if choice_lower not in choices:
            return await ctx.send(embed=discord.Embed(title="خطأ", description="اكتب: `rock/paper/scissors` أو `حجر/ورقة/مقص`", color=ERROR_COLOR))

        bot_choice = random.choice(list(choices.keys()))
        user_emoji = choices[choice_lower]
        bot_emoji = choices[bot_choice]

        if choice_lower == bot_choice:
            result = "تعادل! 🤝"
            color = EMBED_COLOR
        elif (choice_lower in ["rock", "حجر"] and bot_choice in ["scissors", "مقص"]) or \
             (choice_lower in ["paper", "ورقة"] and bot_choice in ["rock", "حجر"]) or \
             (choice_lower in ["scissors", "مقص"] and bot_choice in ["paper", "ورقة"]):
            result = "فزت! 🎉"
            color = SUCCESS_COLOR
        else:
            result = "خسرت! 😢"
            color = ERROR_COLOR

        embed = discord.Embed(title="🎮 حجر ورقة مقص", color=color)
        embed.add_field(name="أنت", value=f"{user_emoji} {choice}", inline=True)
        embed.add_field(name="البوت", value=f"{bot_emoji} {bot_choice}", inline=True)
        embed.add_field(name="النتيجة", value=result, inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="rate", description="قيّم شيئاً من 1 إلى 10")
    async def rate(self, ctx, *, thing: str):
        rating = random.randint(1, 10)
        bar = "🟩" * rating + "⬜" * (10 - rating)
        embed = discord.Embed(title="📊 التقييم", color=EMBED_COLOR)
        embed.add_field(name=f"أقيّم {thing}", value=f"**{rating}/10**\n{bar}", inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="coinflip", description="قلب العملة")
    async def coinflip(self, ctx):
        result = random.choice(["HEADS 🪙", "TAILS 🪙"])
        await ctx.send(embed=discord.Embed(title="🪙 قلب العملة", description=f"**{result}**", color=EMBED_COLOR))

    @commands.hybrid_command(name="meme", description="ارميم عشوائي")
    async def meme(self, ctx):
        memes = [
            "When you push to production on Friday... 🤦‍♂️",
            "99 bugs in the code... fix one... 127 bugs in the code 😅",
            "It's not a bug, it's a feature! 🐛",
            "I don't always test, but when I do, I do it in production 🎯",
            "There's no place like 127.0.0.1 🏠",
            "Programming is like magic... except it actually works sometimes ✨",
            "Have you tried turning it off and on again? 🔄",
            "It works on my machine! 💻",
            "A SQL query walks into a bar, sees two tables, and asks... 🍺",
            "Why do programmers prefer dark mode? Because light attracts bugs! 🌙"
        ]
        embed = discord.Embed(title="😂 ميم", description=random.choice(memes), color=EMBED_COLOR)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="hug", description="ودّع عضو")
    async def hug(self, ctx, member: discord.Member):
        if member.id == ctx.author.id:
            return await ctx.send(embed=discord.Embed(title="🤗", description="**{ctx.author.mention}** يحتضن نفسه! هذا حزن 😢", color=EMBED_COLOR))
        embed = discord.Embed(description=f"**{ctx.author.mention}** يحتضن **{member.mention}**! 🤗💕", color=EMBED_COLOR)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="slap", description="صفّق عضو")
    async def slap(self, ctx, member: discord.Member):
        embed = discord.Embed(description=f"**{ctx.author.mention}** يصفق **{member.mention}**! 👋😤", color=EMBED_COLOR)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="say", description="البوت يكرر كلامك")
    async def say(self, ctx, *, text: str):
        await ctx.message.delete()
        await ctx.send(text)

    @commands.hybrid_command(name="embed", description="ارسل embed")
    async def embed_cmd(self, ctx, title: str, *, description: str):
        embed = discord.Embed(title=title, description=description, color=EMBED_COLOR)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Fun(bot))
