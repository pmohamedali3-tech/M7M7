import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp
import os
import re
from collections import deque
from config import EMBED_COLOR, ERROR_COLOR, SUCCESS_COLOR, WARNING_COLOR

FFMPEG_PATH = r"C:\Users\compumarts\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin\ffmpeg.exe"

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

queues = {}
now_playing = {}


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_queue(self, guild_id):
        if guild_id not in queues:
            queues[guild_id] = deque()
        return queues[guild_id]

    async def search_youtube(self, query):
        loop = asyncio.get_event_loop()
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch1',
            'source_address': '0.0.0.0',
        }
        return await loop.run_in_executor(None, self._search, query, ydl_opts)

    def _search(self, query, ydl_opts):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(query, download=False)
                if 'entries' in info:
                    info = info['entries'][0]
                return {
                    'url': info['url'],
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'webpage_url': info.get('webpage_url', ''),
                    'requester': None,
                }
            except Exception as e:
                return None

    async def search_spotify(self, query):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._search_spotify, query)

    def _search_spotify(self, query):
        spotify_url_pattern = r'open\.spotify\.com/(track|playlist|album)/([a-zA-Z0-9]+)'
        match = re.search(spotify_url_pattern, query)

        if match:
            content_type = match.group(1)
            content_id = match.group(2)
            return {'type': content_type, 'id': content_id, 'url': query}
        else:
            return {'type': 'search', 'query': query, 'url': query}

    async def play_song(self, ctx, song_info):
        vc = ctx.voice_client
        if not vc:
            return

        source = discord.FFmpegOpusAudio(song_info['url'], **FFMPEG_OPTIONS)

        def after_playing(error):
            if error:
                print(f'Player error: {error}')
            coro = self.play_next(ctx.guild)
            asyncio.run_coroutine_threadsafe(coro, self.bot.loop)

        now_playing[ctx.guild.id] = song_info
        vc.play(source, after=after_playing)

        embed = discord.Embed(
            title=" đang phát",
            description=f"**{song_info['title']}**",
            color=EMBED_COLOR
        )
        if song_info.get('duration'):
            mins, secs = divmod(song_info['duration'], 60)
            embed.add_field(name="المدة", value=f"{mins}:{secs:02d}", inline=True)
        embed.add_field(name="طلبها", value=song_info['requester'].display_name, inline=True)
        embed.set_footer(text="اكتب !skip للتخطي | !stop للإيقاف")
        await ctx.send(embed=embed)

    async def play_next(self, guild):
        queue = self.get_queue(guild.id)
        if queue:
            song_info = queue.popleft()
            vc = guild.voice_client
            if vc and vc.is_connected():
                await self.play_song_direct(guild, vc, song_info)

    async def play_song_direct(self, guild, vc, song_info):
        source = discord.FFmpegOpusAudio(song_info['url'], **FFMPEG_OPTIONS)

        def after_playing(error):
            if error:
                print(f'Player error: {error}')
            coro = self.play_next(guild)
            asyncio.run_coroutine_threadsafe(coro, self.bot.loop)

        now_playing[guild.id] = song_info
        vc.play(source, after=after_playing)

    @commands.hybrid_command(name="join", description="ادخل روم صوتي")
    async def join(self, ctx):
        if not ctx.author.voice:
            return await ctx.send(embed=discord.Embed(
                title="خطأ",
                description="لازم تكون في روم صوتي الأول!",
                color=ERROR_COLOR
            ))
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.send(embed=discord.Embed(
            description=f"ادخلت {channel.mention}",
            color=SUCCESS_COLOR
        ))

    @commands.hybrid_command(name="play", description="شغّل أغنية (اسم أو رابط YouTube أو Spotify)")
    async def play(self, ctx, *, query: str):
        if not ctx.author.voice:
            return await ctx.send(embed=discord.Embed(
                title="خطأ",
                description="لازم تكون في روم صوتي!",
                color=ERROR_COLOR
            ))

        vc = ctx.voice_client
        if not vc:
            vc = await ctx.author.voice.channel.connect()
        elif vc.channel != ctx.author.voice.channel:
            await vc.move_to(ctx.author.voice.channel)

        async with ctx.typing():
            spotify_info = await self.search_spotify(query)

            if spotify_info['type'] in ('track', 'playlist', 'album'):
                search_query = f"ytsearch:{spotify_info['id']}"
            else:
                search_query = query

            song_info = await self.search_youtube(search_query)
            if not song_info:
                return await ctx.send(embed=discord.Embed(
                    title="خطأ",
                    description="مقدرتش ألاقي الأغنية!",
                    color=ERROR_COLOR
                ))

            song_info['requester'] = ctx.author

            if vc.is_playing() or vc.is_paused():
                queue = self.get_queue(ctx.guild.id)
                queue.append(song_info)
                embed = discord.Embed(
                    title="تمت الإضافة للقائمة",
                    description=f"**{song_info['title']}**\nالمركز: #{len(queue)}",
                    color=EMBED_COLOR
                )
                if song_info.get('duration'):
                    mins, secs = divmod(song_info['duration'], 60)
                    embed.add_field(name="المدة", value=f"{mins}:{secs:02d}", inline=True)
                return await ctx.send(embed=embed)

            await self.play_song(ctx, song_info)

    @commands.hybrid_command(name="skip", description="تخطّي الأغنية الحالية")
    async def skip(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.send(embed=discord.Embed(
                title="خطأ",
                description="مفيش أغنية شغالة!",
                color=ERROR_COLOR
            ))
        vc.stop()

    @commands.hybrid_command(name="stop", description="وقف الموسيقى ومسح القائمة")
    async def stop(self, ctx):
        vc = ctx.voice_client
        if not vc:
            return await ctx.send(embed=discord.Embed(
                title="خطأ",
                description="مفيش بوت في روم صوتي!",
                color=ERROR_COLOR
            ))
        queue = self.get_queue(ctx.guild.id)
        queue.clear()
        if ctx.guild.id in now_playing:
            del now_playing[ctx.guild.id]
        vc.stop()
        await ctx.send(embed=discord.Embed(
            title="تم الإيقاف",
            description="الموسيقى تتوقفت والقائمة اتمسحت.",
            color=SUCCESS_COLOR
        ))

    @commands.hybrid_command(name="pause", description="وقف مؤقت")
    async def pause(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.send(embed=discord.Embed(
                title="خطأ",
                description="مفيش أغنية شغالة!",
                color=ERROR_COLOR
            ))
        vc.pause()
        await ctx.send(embed=discord.Embed(
            title="تم الإيقاف المؤقت",
            description="اكتب !resume عشان تكمل.",
            color=WARNING_COLOR
        ))

    @commands.hybrid_command(name="resume", description="كمل الموسيقى")
    async def resume(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_paused():
            return await ctx.send(embed=discord.Embed(
                title="خطأ",
                description="مفيش أغنية واقفة!",
                color=ERROR_COLOR
            ))
        vc.resume()
        await ctx.send(embed=discord.Embed(
            title="تم الاستئناف",
            description="الموسيقى بتكمل.",
            color=SUCCESS_COLOR
        ))

    @commands.hybrid_command(name="queue", description="عرض قائمة التشغيل")
    async def queue_list(self, ctx):
        queue = self.get_queue(ctx.guild.id)
        if not queue:
            return await ctx.send(embed=discord.Embed(
                title="القائمة فاضية",
                description="مفيش أغاني في القائمة.",
                color=ERROR_COLOR
            ))

        embed = discord.Embed(
            title=f"قائمة التشغيل ({len(queue)} أغنية)",
            color=EMBED_COLOR
        )
        for i, song in enumerate(list(queue)[:10], 1):
            duration = ""
            if song.get('duration'):
                mins, secs = divmod(song['duration'], 60)
                duration = f" [{mins}:{secs:02d}]"
            embed.add_field(
                name=f"#{i}",
                value=f"**{song['title']}**{duration}\nطلبها: {song['requester'].display_name}",
                inline=False
            )
        if len(queue) > 10:
            embed.set_footer(text=f"... ועוד {len(queue) - 10} أغنية")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="nowplaying", alias="np", description="الاغنية الحالية")
    async def now_playing_cmd(self, ctx):
        song = now_playing.get(ctx.guild.id)
        if not song:
            return await ctx.send(embed=discord.Embed(
                title="خطأ",
                description="مفيش أغنية شغالة!",
                color=ERROR_COLOR
            ))

        embed = discord.Embed(
            title="الاغنية الحالية",
            description=f"**{song['title']}**",
            color=EMBED_COLOR
        )
        if song.get('duration'):
            mins, secs = divmod(song['duration'], 60)
            embed.add_field(name="المدة", value=f"{mins}:{secs:02d}", inline=True)
        embed.add_field(name="طلبها", value=song['requester'].display_name, inline=True)
        if song.get('thumbnail'):
            embed.set_thumbnail(url=song['thumbnail'])
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="leave", description="اخرج من الروم الصوتي")
    async def leave(self, ctx):
        vc = ctx.voice_client
        if not vc:
            return await ctx.send(embed=discord.Embed(
                title="خطأ",
                description="مفيش بوت في روم صوتي!",
                color=ERROR_COLOR
            ))
        queue = self.get_queue(ctx.guild.id)
        queue.clear()
        if ctx.guild.id in now_playing:
            del now_playing[ctx.guild.id]
        await vc.disconnect()
        await ctx.send(embed=discord.Embed(
            title="تم الخروج",
            description="البوت خرج من الروم الصوتي.",
            color=SUCCESS_COLOR
        ))


async def setup(bot):
    await bot.add_cog(Music(bot))
