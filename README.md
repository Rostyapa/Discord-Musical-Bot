# Discord Music Bot

This bot allows you to play music in Discord voice channels, supporting tracks and playlists from YouTube, YouTube Music, Spotify, and SoundCloud. You can deploy the bot on a hosting service (e.g., Railway), run it locally on your computer, or use Docker.

## Features
- Play tracks and playlists from YouTube, YouTube Music, Spotify, and SoundCloud.
- Control playback: pause, resume, skip, restart tracks, and adjust volume.
- Queue management: add tracks to the queue and view the queue.
- Playlist support: the bot can play entire playlists from various platforms.

## Requirements
To run the bot, you will need:
- Python 3.8 or higher (3.11 recommended).
- A Discord account and a bot token.
- A Spotify Developer account (to obtain `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`).
- A hosting service (e.g., Railway), a local computer, or Docker to run the bot.
- (Optional) Cookies for SoundCloud and YouTube if you want to play private tracks or playlists.

## Setup and Configuration

### 1. Clone the Repository
Clone this repository to your computer or upload it to your hosting service:
```
git clone https://github.com/your-username/discord-music-bot.git
cd discord-music-bot
```
# 2. Configure Tokens and API Keys
