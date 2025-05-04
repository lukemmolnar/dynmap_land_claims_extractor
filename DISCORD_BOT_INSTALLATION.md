# Discord Bot Installation Guide

This guide will help you set up the Discord notification bot for monitoring new images in the claim_disappearances folder.

## Prerequisites

- Python 3.6 or higher
- pip (Python package manager)
- A Discord bot token (already configured in the systemd service file)
- Discord server with a channel where images will be sent

## Installation Steps

### 1. Install Required Dependencies

Add the new dependencies to your Python environment:

```bash
pip install discord.py watchdog python-dotenv
```

Or simply update your existing requirements:

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables (.env file)

The bot now uses python-dotenv to load environment variables from a .env file. You can either:

1. Create a .env file in the current directory:

```bash
cd /home/website/dynmap_land_claims_extractor
echo "DISCORD_TOKEN=your_bot_token_here" > .env
chmod 600 .env  # Secure the file so only you can read it
```

2. Or use your existing .env file at ~/agelbub_bot/.env (the bot will automatically check this location).

### 3. Configure the Discord Channel ID

Edit the `discord_notification_bot.py` file and replace the placeholder channel ID with your actual Discord channel ID:

```python
# Find this line in discord_notification_bot.py
DISCORD_CHANNEL_ID = 1234567890123456789  # Replace with your channel ID
```

To get your channel ID in Discord:
1. Enable Developer Mode in Discord (User Settings > App Settings > Advanced > Developer Mode)
2. Right-click on the channel where you want to send the images
3. Select "Copy ID"
4. Paste this ID in place of the placeholder in the script

### 4. Set Up the Systemd Service

1. Copy the service file to the systemd directory:

```bash
sudo cp discord-notification-bot.service /etc/systemd/system/
```

Or if you're using a different name for your service:

```bash
sudo cp discord-notification-bot.service /etc/systemd/system/discord-bot.service
```

2. Reload the systemd daemon:

```bash
sudo systemctl daemon-reload
```

3. Enable the service to start on boot:

```bash
sudo systemctl enable discord-bot
```

4. Start the service:

```bash
sudo systemctl start discord-bot
```

## Verifying Installation

Check if the service is running correctly:

```bash
sudo systemctl status discord-notification-bot
```

You should see "active (running)" in the output.

## Monitoring Logs

The bot will log its activity to `discord_notification_bot.log` in the working directory. You can view the logs with:

```bash
tail -f /home/website/dynmap_land_claims_extractor/discord_notification_bot.log
```

## Testing the Bot

To test if the bot is working correctly, you can add a new image to one of the claim_disappearances subfolders and check if it appears in your Discord channel.

## Troubleshooting

If the bot isn't working as expected:

1. Check the log file for errors
2. Verify the Discord token is correct in the service file
3. Make sure the bot has permissions to access the specified channel
4. Ensure the path to the claim_disappearances folder is correct
5. Check that the bot has proper permissions on Discord (it needs permissions to read/send messages and attach files)

## Stopping or Restarting the Bot

To stop the service:

```bash
sudo systemctl stop discord-notification-bot
```

To restart the service:

```bash
sudo systemctl restart discord-notification-bot
