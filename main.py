import discord
from discord import app_commands, ui
import yt_dlp
import asyncio
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from collections import deque
import logging
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Подавляем предупреждения от yt-dlp
yt_dlp.utils.std_headers['User-Agent'] = 'Mozilla/5.0'
yt_dlp.utils.std_headers['Accept-Language'] = 'en-US,en;q=0.9'

# Проверяем токен Discord
token = os.getenv('DISCORD_TOKEN')
if not token:
    raise ValueError("DISCORD_TOKEN не задан в переменных окружения!")

# Настраиваем Spotify
spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
if not spotify_client_id or not spotify_client_secret:
    raise ValueError("SPOTIFY_CLIENT_ID или SPOTIFY_CLIENT_SECRET не заданы!")
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret))

# Настраиваем intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Настройки для yt-dlp и FFmpeg
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'extract_flat': True,
}
YDL_OPTIONS_FULL = {
    'format': 'bestaudio/best',
    'noplaylist': False,
    'quiet': True,
    'no_warnings': True,
}
YDL_OPTIONS_SOUNDCLOUD = {
    'format': 'bestaudio/best',
    'noplaylist': False,
    'quiet': True,
    'no_warnings': True,
    'extract_flat': True,
    'cookiefile': 'soundcloud_cookies.txt',  # Укажи путь к файлу с cookies
}
YDL_OPTIONS_SOUNDCLOUD_FULL = {
    'format': 'bestaudio/best',
    'noplaylist': False,
    'quiet': True,
    'no_warnings': True,
    'cookiefile': 'soundcloud_cookies.txt',
}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

# Укажи путь к FFmpeg (замени на свой путь)
FFMPEG_PATH = "M:/ffmpeg-master-latest-win64-gpl-shared/bin/ffmpeg.exe"  # Для Windows
# FFMPEG_PATH = "/usr/bin/ffmpeg"  # Для Linux
# FFMPEG_PATH = "/usr/local/bin/ffmpeg"  # Для macOS

# Очередь и состояние для каждого сервера
queues = {}
last_button_press = {}
current_track = {}
added_by = {}
current_track_url = {}
control_messages = {}
update_tasks = {}

@client.event
async def on_ready():
    await tree.sync()
    logging.info(f'Бот {client.user} успешно запущен и подключён! Команды синхронизированы.')

async def get_youtube_url(query):
    loop = asyncio.get_event_loop()
    with yt_dlp.YoutubeDL(YDL_OPTIONS_FULL) as ydl:
        try:
            result = await loop.run_in_executor(None, lambda: ydl.extract_info(query, download=False))
            if 'entries' in result and result['entries']:
                return result['entries'][0]['url'], result['entries'][0]['title']
            elif 'url' in result:
                return result['url'], result['title']
        except Exception as e:
            logging.error(f"Ошибка поиска YouTube: {e}")
    return None, None

async def get_youtube_playlist_urls(playlist_url):
    loop = asyncio.get_event_loop()
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            result = await loop.run_in_executor(None, lambda: ydl.extract_info(playlist_url, download=False))
            if 'entries' in result:
                return [(entry['url'], entry.get('title', 'Unknown Title')) for entry in result['entries']]
            return []
        except Exception as e:
            logging.error(f"Ошибка извлечения URL плейлиста YouTube: {e}")
            return []

async def get_soundcloud_url(url):
    loop = asyncio.get_event_loop()
    with yt_dlp.YoutubeDL(YDL_OPTIONS_SOUNDCLOUD_FULL) as ydl:
        try:
            result = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            if 'entries' in result and result['entries']:
                return result['entries'][0]['url'], result['entries'][0]['title']
            elif 'url' in result:
                return result['url'], result['title']
        except Exception as e:
            logging.error(f"Ошибка поиска SoundCloud: {e}")
    return None, None

async def get_soundcloud_playlist_urls(playlist_url):
    loop = asyncio.get_event_loop()
    with yt_dlp.YoutubeDL(YDL_OPTIONS_SOUNDCLOUD) as ydl:
        try:
            result = await loop.run_in_executor(None, lambda: ydl.extract_info(playlist_url, download=False))
            if 'entries' in result:
                return [(entry['url'], entry.get('title', 'Unknown Title')) for entry in result['entries']]
            return []
        except Exception as e:
            logging.error(f"Ошибка извлечения URL плейлиста SoundCloud: {e}")
            return []

def get_spotify_track_info(track_url):
    track = sp.track(track_url)
    return f"{track['artists'][0]['name']} - {track['name']}"

def get_spotify_playlist_tracks(playlist_url):
    playlist = sp.playlist_tracks(playlist_url)
    return [f"{item['track']['artists'][0]['name']} - {item['track']['name']}" for item in playlist['items']]

async def update_control_message(guild_id, user_avatar):
    while guild_id in control_messages:
        if guild_id not in control_messages:
            return
        message = control_messages.get(guild_id)
        if not message:
            return
        embed = discord.Embed(title="Управление музыкой", description=f"🎵 Сейчас играет: **{current_track.get(guild_id, 'Ничего не играет')}**", color=discord.Color.blue())
        embed.set_thumbnail(url=user_avatar)
        embed.set_footer(text=f"В очереди: {len(queues.get(guild_id, deque()))} треков | Добавлено: {added_by.get(guild_id, 'Неизвестно')}")
        try:
            await message.edit(embed=embed)
        except Exception as e:
            logging.error(f"Ошибка обновления сообщения: {e}")
            break
        await asyncio.sleep(30)

async def play_next(interaction: discord.Interaction):
    vc = discord.utils.get(client.voice_clients, guild=interaction.guild)
    if not vc or not queues.get(interaction.guild.id):
        return

    queue = queues[interaction.guild.id]
    if queue and not vc.is_playing():
        audio_url, title = queue.popleft()
        current_track[interaction.guild.id] = title
        current_track_url[interaction.guild.id] = audio_url
        try:
            # Оборачиваем FFmpegPCMAudio в PCMVolumeTransformer для управления громкостью
            source = discord.FFmpegPCMAudio(audio_url, executable=FFMPEG_PATH, **FFMPEG_OPTIONS)
            source = discord.PCMVolumeTransformer(source, volume=1.0)  # Начальная громкость 100%
            vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(interaction), client.loop))
        except Exception as e:
            logging.error(f"Ошибка воспроизведения: {e}")
            await interaction.followup.send(f"Ошибка воспроизведения: {e}")
    elif not queue:
        await interaction.followup.send("Очередь пуста!")

async def process_playlist(interaction: discord.Interaction, tracks, is_spotify=True, is_soundcloud=False):
    queue = queues[interaction.guild.id]
    for track in tracks:
        if is_spotify:
            audio_url, title = await get_youtube_url(track)
        elif is_soundcloud:
            audio_url, title = await get_soundcloud_url(track[0])
        else:
            audio_url, title = await get_youtube_url(track[0])
        if audio_url:
            queue.append((audio_url, title))
            logging.info(f"Добавлен в очередь: {title}")

@app_commands.command(name="play", description="Воспроизвести трек или плейлист по URL (Spotify, YouTube, YouTube Music, SoundCloud)")
async def play(interaction: discord.Interaction, url: str):
    await interaction.response.defer()

    if not interaction.user.voice:
        await interaction.followup.send("Ты должен быть в голосовом канале!")
        return

    voice_channel = interaction.user.voice.channel
    try:
        vc = await voice_channel.connect()
        logging.info(f"Подключён к голосовому каналу: {voice_channel.name}")
    except discord.ClientException:
        vc = discord.utils.get(client.voice_clients, guild=interaction.guild)

    if interaction.guild.id not in queues:
        queues[interaction.guild.id] = deque()

    added_by[interaction.guild.id] = interaction.user.name

    try:
        if 'spotify.com/track' in url:
            track_query = get_spotify_track_info(url)
            audio_url, title = await get_youtube_url(track_query)
            if not audio_url:
                await interaction.followup.send("Не удалось найти трек на YouTube.")
                return
            queues[interaction.guild.id].append((audio_url, title))
            current_track[interaction.guild.id] = title
            current_track_url[interaction.guild.id] = audio_url

        elif 'spotify.com/playlist' in url:
            tracks = get_spotify_playlist_tracks(url)
            await interaction.followup.send(f"Найден плейлист Spotify с {len(tracks)} треками. Начинаю обработку...")
            audio_url, title = await get_youtube_url(tracks[0])
            if audio_url:
                queues[interaction.guild.id].append((audio_url, title))
                current_track[interaction.guild.id] = title
                current_track_url[interaction.guild.id] = audio_url
                asyncio.create_task(process_playlist(interaction, tracks[1:], is_spotify=True))
            else:
                await interaction.followup.send("Не удалось найти первый трек на YouTube.")
                return

        elif 'youtube.com/playlist' in url or 'music.youtube.com/playlist' in url:
            tracks = await get_youtube_playlist_urls(url)
            if not tracks:
                await interaction.followup.send("Не удалось найти плейлист YouTube.")
                return
            audio_url, title = await get_youtube_url(tracks[0][0])
            if not audio_url:
                await interaction.followup.send("Не удалось найти первый трек плейлиста YouTube.")
                return
            queues[interaction.guild.id].append((audio_url, title))
            current_track[interaction.guild.id] = title
            current_track_url[interaction.guild.id] = audio_url
            await interaction.followup.send(f"Найден плейлист YouTube с {len(tracks)} треками. Начинаю обработку...")
            if len(tracks) > 1:
                asyncio.create_task(process_playlist(interaction, tracks[1:], is_spotify=False))

        elif 'soundcloud.com' in url:
            if '/sets/' in url:  # Плейлист SoundCloud
                tracks = await get_soundcloud_playlist_urls(url)
                if not tracks:
                    await interaction.followup.send("Не удалось найти плейлист на SoundCloud.")
                    return
                audio_url, title = await get_soundcloud_url(tracks[0][0])
                if not audio_url:
                    await interaction.followup.send("Не удалось найти первый трек плейлиста SoundCloud.")
                    return
                queues[interaction.guild.id].append((audio_url, title))
                current_track[interaction.guild.id] = title
                current_track_url[interaction.guild.id] = audio_url
                await interaction.followup.send(f"Найден плейлист SoundCloud с {len(tracks)} треками. Начинаю обработку...")
                if len(tracks) > 1:
                    asyncio.create_task(process_playlist(interaction, tracks[1:], is_spotify=False, is_soundcloud=True))
            else:  # Одиночный трек SoundCloud
                audio_url, title = await get_soundcloud_url(url)
                if not audio_url:
                    await interaction.followup.send("Не удалось найти трек на SoundCloud.")
                    return
                queues[interaction.guild.id].append((audio_url, title))
                current_track[interaction.guild.id] = title
                current_track_url[interaction.guild.id] = audio_url

        else:
            audio_url, title = await get_youtube_url(url)
            if not audio_url:
                await interaction.followup.send("Не удалось найти трек на YouTube.")
                return
            queues[interaction.guild.id].append((audio_url, title))
            current_track[interaction.guild.id] = title
            current_track_url[interaction.guild.id] = audio_url

        embed = discord.Embed(title="Управление музыкой", description=f"🎵 Сейчас играет: **{current_track[interaction.guild.id]}**", color=discord.Color.blue())
        embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
        embed.set_footer(text=f"В очереди: {len(queues[interaction.guild.id])} треков | Добавлено: {added_by[interaction.guild.id]}")

        view = MusicControls()
        message = await interaction.followup.send(embed=embed, view=view)
        control_messages[interaction.guild.id] = message

        # Запускаем задачу обновления сообщения каждые 30 секунд
        user_avatar = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
        update_task = asyncio.create_task(update_control_message(interaction.guild.id, user_avatar))
        update_tasks[interaction.guild.id] = update_task

        if not vc.is_playing():
            await play_next(interaction)

    except Exception as e:
        logging.error(f"Ошибка при воспроизведении: {e}")
        await interaction.followup.send(f"Не удалось воспроизвести: {e}")

class MusicControls(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        user_id = interaction.user.id
        current_time = time.time()
        last_press = last_button_press.get(user_id, 0)

        if current_time - last_press < 3:
            await interaction.response.send_message("Подожди 3 секунды перед следующим нажатием!", ephemeral=True)
            return False

        last_button_press[user_id] = current_time
        return True

    @ui.button(emoji="<:Play:1355147643600375969>", style=discord.ButtonStyle.grey)
    async def resume_button(self, interaction: discord.Interaction, button: ui.Button):
        vc = discord.utils.get(client.voice_clients, guild=interaction.guild)
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("Воспроизведение возобновлено.", ephemeral=True)
        else:
            await interaction.response.send_message("Музыка не на паузе.", ephemeral=True)

    @ui.button(emoji="<:Pause:1355147640836198531>", style=discord.ButtonStyle.grey)
    async def pause_button(self, interaction: discord.Interaction, button: ui.Button):
        vc = discord.utils.get(client.voice_clients, guild=interaction.guild)
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("Музыка на паузе.", ephemeral=True)
        else:
            await interaction.response.send_message("Сейчас ничего не играет.", ephemeral=True)

    @ui.button(emoji="<:Skip:1355147642077970473>", style=discord.ButtonStyle.grey)
    async def skip_button(self, interaction: discord.Interaction, button: ui.Button):
        vc = discord.utils.get(client.voice_clients, guild=interaction.guild)
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("Трек пропущен.", ephemeral=True)
            await play_next(interaction)
        else:
            await interaction.response.send_message("Сейчас ничего не играет.", ephemeral=True)

    @ui.button(emoji="<:restart:1355147638215016539>", style=discord.ButtonStyle.grey)
    async def restart_button(self, interaction: discord.Interaction, button: ui.Button):
        vc = discord.utils.get(client.voice_clients, guild=interaction.guild)
        if vc and vc.is_playing() and interaction.guild.id in current_track_url:
            vc.stop()
            audio_url = current_track_url[interaction.guild.id]
            title = current_track[interaction.guild.id]
            source = discord.FFmpegPCMAudio(audio_url, executable=FFMPEG_PATH, **FFMPEG_OPTIONS)
            source = discord.PCMVolumeTransformer(source, volume=vc.source.volume if vc.source else 1.0)  # Сохраняем текущую громкость
            vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(interaction), client.loop))
            await interaction.response.send_message("Трек перезапущен.", ephemeral=True)
        else:
            await interaction.response.send_message("Сейчас ничего не играет или трек недоступен.", ephemeral=True)

    @ui.button(emoji="❤️", style=discord.ButtonStyle.grey)
    async def link_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("Перейди по ссылке: <https://example.com>", ephemeral=True)

    @ui.button(emoji="<:stopbutton:1355147611375407185>", style=discord.ButtonStyle.grey)
    async def clear_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.guild.id in queues:
            queues[interaction.guild.id].clear()
            await interaction.response.send_message("Очередь очищена.", ephemeral=True)
        else:
            await interaction.response.send_message("Очередь уже пуста!", ephemeral=True)

    @ui.button(emoji="🏗️", style=discord.ButtonStyle.grey)
    async def queue_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.guild.id not in queues or not queues[interaction.guild.id]:
            await interaction.response.send_message("Очередь пуста!", ephemeral=True)
            return
        queue_list = "\n".join([f"{i+1}. {title}" for i, (_, title) in enumerate(queues[interaction.guild.id])])
        await interaction.response.send_message(f"Текущая очередь:\n{queue_list}", ephemeral=True)

    @ui.button(emoji="<:exit:1355147639603069139>", style=discord.ButtonStyle.grey)
    async def leave_button(self, interaction: discord.Interaction, button: ui.Button):
        vc = discord.utils.get(client.voice_clients, guild=interaction.guild)
        if vc:
            await vc.disconnect()
            if interaction.guild.id in queues:
                del queues[interaction.guild.id]
            if interaction.guild.id in current_track:
                del current_track[interaction.guild.id]
            if interaction.guild.id in current_track_url:
                del current_track_url[interaction.guild.id]
            if interaction.guild.id in added_by:
                del added_by[interaction.guild.id]
            if interaction.guild.id in control_messages:
                del control_messages[interaction.guild.id]
            if interaction.guild.id in update_tasks:
                update_tasks[interaction.guild.id].cancel()
                del update_tasks[interaction.guild.id]
            await interaction.response.send_message("Бот покинул канал.", ephemeral=True)
            await interaction.message.delete()
            self.stop()
        else:
            await interaction.response.send_message("Я не в голосовом канале!", ephemeral=True)

    @ui.button(emoji="👍", style=discord.ButtonStyle.grey)
    async def volume_up_button(self, interaction: discord.Interaction, button: ui.Button):
        vc = discord.utils.get(client.voice_clients, guild=interaction.guild)
        if vc and vc.source:
            current_volume = vc.source.volume
            new_volume = min(current_volume + 0.1, 1.0)  # Увеличиваем громкость на 10%, максимум 100%
            vc.source.volume = new_volume
            await interaction.response.send_message(f"Громкость увеличена до {int(new_volume * 100)}%.", ephemeral=True)
        else:
            await interaction.response.send_message("Бот не в голосовом канале или ничего не играет!", ephemeral=True)

    @ui.button(emoji="👉", style=discord.ButtonStyle.grey)
    async def volume_down_button(self, interaction: discord.Interaction, button: ui.Button):
        vc = discord.utils.get(client.voice_clients, guild=interaction.guild)
        if vc and vc.source:
            current_volume = vc.source.volume
            new_volume = max(current_volume - 0.1, 0.0)  # Уменьшаем громкость на 10%, минимум 0%
            vc.source.volume = new_volume
            await interaction.response.send_message(f"Громкость уменьшена до {int(new_volume * 100)}%.", ephemeral=True)
        else:
            await interaction.response.send_message("Бот не в голосовом канале или ничего не играет!", ephemeral=True)

# Регистрируем команду
tree.add_command(play)

try:
    client.run(token)
except Exception as e:
    logging.error(f"Ошибка запуска бота: {e}")