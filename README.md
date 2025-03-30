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
```bash
git clone https://github.com/your-username/discord-music-bot.git
cd discord-music-bot
2. Configure Tokens and API Keys
You need to set up the following environment variables:

DISCORD_TOKEN: Your Discord bot token.
SPOTIFY_CLIENT_ID: Your Spotify Client ID.
SPOTIFY_CLIENT_SECRET: Your Spotify Client Secret.
How to Obtain Tokens:
Discord Token:
Go to the Discord Developer Portal.
Create a new application and add a bot.
Copy the bot token and save it as DISCORD_TOKEN.
Ensure the bot has the following Intents enabled: message_content and voice_states.
Spotify Client ID and Client Secret:
Go to the Spotify Developer Dashboard.
Create a new application.
Copy the Client ID and Client Secret and save them as SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET.
If your app is in development mode, add your Spotify account to the list of users in the "Users and Access" section.
Setting Up Environment Variables:
Locally: Create a .env file in the project root and add:
text

Collapse

Wrap

Copy
DISCORD_TOKEN=your_discord_token
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
Then install the python-dotenv library (pip install python-dotenv) and add the following to the top of main.py:
python

Collapse

Wrap

Copy
from dotenv import load_dotenv
load_dotenv()
On Railway: In the "Variables" section, add:
text

Collapse

Wrap

Copy
DISCORD_TOKEN=your_discord_token
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
With Docker: Pass the environment variables when running the container (see the "Deployment with Docker" section).
3. (Optional) Configure Cookies for SoundCloud and YouTube
If you want to play private tracks or playlists from SoundCloud or YouTube, you need to set up cookies.

For SoundCloud:
Log in to your SoundCloud account in a browser.
Open the developer tools (F12) → "Network" tab.
Refresh the page and find a request to soundcloud.com.
Copy the cookies from the request headers (or use an extension like EditThisCookie).
Open the soundcloud_cookies.txt file and paste the cookies in Netscape format:
text

Collapse

Wrap

Copy
# Netscape HTTP Cookie File
.soundcloud.com    TRUE    /    FALSE    0    key    value
Replace key and value with the actual cookie values.
For YouTube:
Log in to your YouTube account.
Similarly, extract cookies using the developer tools.
Paste them into the youtube_cookies.txt file in the same format.
Deployment
Option 1: Local Deployment
Install dependencies:
bash

Collapse

Wrap

Copy
pip install -r requirements.txt
Ensure FFmpeg is installed on your computer:
Windows: Download FFmpeg from the official website and add it to your PATH.
Linux: Install via your package manager, e.g., sudo apt install ffmpeg.
macOS: Install via Homebrew, brew install ffmpeg.
Run the bot:
bash

Collapse

Wrap

Copy
python main.py
Option 2: Deployment on Railway
Create a project on Railway.
Connect your GitHub repository.
Add the environment variables (DISCORD_TOKEN, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET) in the "Variables" section.
Railway will automatically build and run the bot using nixpacks.toml.
Option 3: Deployment with Docker
Ensure Docker is installed:
Windows/macOS: Install Docker Desktop.
Linux: Install Docker via your package manager, e.g., sudo apt install docker.io.
Build the Docker image:
bash

Collapse

Wrap

Copy
docker build -t discord-music-bot .
Run the container, passing the environment variables:
bash

Collapse

Wrap

Copy
docker run -d \
  -e DISCORD_TOKEN=your_discord_token \
  -e SPOTIFY_CLIENT_ID=your_spotify_client_id \
  -e SPOTIFY_CLIENT_SECRET=your_spotify_client_secret \
  discord-music-bot
The -d flag runs the container in detached mode.
The -e flag passes environment variables to the container.
Note:
If you want to deploy the bot on a Docker-supported hosting service (e.g., Fly.io, Render, or your own server), push the built image to Docker Hub or use docker-compose for more complex setups.

Usage
Invite the bot to your Discord server:
In the Discord Developer Portal, go to your application → "OAuth2" → "URL Generator".
Select scopes: bot and applications.commands.
Select permissions: Connect, Speak, Send Messages, Embed Links.
Copy the generated URL and use it to invite the bot.
Join a voice channel on your server.
Use the /play command to play music:
Single Track:
text

Collapse

Wrap

Copy
/play https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT
Playlist:
text

Collapse

Wrap

Copy
/play https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
YouTube:
text

Collapse

Wrap

Copy
/play https://www.youtube.com/watch?v=dQw4w9WgXcQ
YouTube Music:
text

Collapse

Wrap

Copy
/play https://music.youtube.com/watch?v=5qap5aO4i9A
SoundCloud:
text

Collapse

Wrap

Copy
/play https://soundcloud.com/artistname/trackname
Search Query:
text

Collapse

Wrap

Copy
/play The Weeknd - Blinding Lights
Use the control buttons to pause, skip, restart tracks, adjust volume, and more.
Troubleshooting
Bot cannot connect to the voice channel:
Ensure the bot has Connect and Speak permissions on the server.
Verify that you are in a voice channel.
Error: "Voice client cannot be created" or "No voice library found":
Ensure PyNaCl is installed (pip install PyNaCl).
Verify that FFmpeg is installed and accessible.
Error: "FFmpeg not found":
Ensure FFmpeg is installed and in your PATH (locally), configured via nixpacks.toml (on Railway), or included in the Docker image.
Spotify Error: "invalid_client":
Verify that SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET are correct.
Ensure your Spotify account is added to the list of users in the Spotify Developer Dashboard.
YouTube Music Playlists Not Working:
If the playlist is a "Radio" playlist (ID starts with RD), the bot may not be able to play it. Try a regular playlist instead.
Configure youtube_cookies.txt to access private playlists.
SoundCloud Not Working:
Ensure the soundcloud_cookies.txt file is populated with your cookies.
Docker: "Cannot connect to the Docker daemon":
Ensure Docker is running (sudo systemctl start docker on Linux, or launch Docker Desktop on Windows/macOS).
Verify you have permission to run Docker (on Linux, add your user to the docker group: sudo usermod -aG docker $USER).
Project Structure
text

Collapse

Wrap

Copy
discord-music-bot/
│
├── main.py               # Main bot code
├── requirements.txt      # Python dependencies
├── nixpacks.toml         # Configuration for Railway
├── soundcloud_cookies.txt # Empty file for SoundCloud cookies
├── youtube_cookies.txt   # Empty file for YouTube cookies
├── Dockerfile            # Dockerfile for building a Docker image
├── README.md             # User instructions
└── .gitignore            # File to exclude unnecessary data
Dependencies
The project's dependencies are listed in requirements.txt:

text

Collapse

Wrap

Copy
discord.py
yt-dlp==2023.12.30
spotipy
PyNaCl==1.5.0
License
This project is licensed under the MIT License. You are free to use, modify, and distribute the code, but the author is not responsible for any issues that may arise. See the LICENSE file for details.

Contact
If you have questions or suggestions, feel free to create an issue in this repository or contact me on Discord: [rostyapa].
