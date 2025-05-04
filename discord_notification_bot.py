import os
import time
import discord
from discord.ext import commands
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("discord_notification_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DiscordNotificationBot")

# Load environment variables from .env file
# Will check for .env in the current directory first, then try the specified path
DEFAULT_ENV_PATH = os.path.expanduser("~/agelbub_bot/.env")

def load_env_file():
    """Attempt to load environment variables from .env files in multiple locations"""
    # Try current directory first
    if os.path.exists(".env"):
        logger.info("Loading .env file from current directory")
        load_dotenv()
        return True
    
    # Try specified path
    if os.path.exists(DEFAULT_ENV_PATH):
        logger.info(f"Loading .env file from {DEFAULT_ENV_PATH}")
        load_dotenv(DEFAULT_ENV_PATH)
        return True
    
    logger.warning("No .env file found")
    return False

# Load environment variables
load_env_file()

# Config
WATCH_DIR = "/home/website/dynmap_land_claims_extractor/claim_disappearances"
DISCORD_CHANNEL_ID = 1368398880844025966  # Replace with your channel ID

# Initialize Discord bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Keep track of processed files to avoid duplicates
processed_files = set()

class ImageEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        # Check if it's an image file
        if not event.src_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            return
            
        # Get the full path
        file_path = Path(event.src_path)
        
        # Avoid processing the same file twice
        if str(file_path) in processed_files:
            return
            
        logger.info(f"New image detected: {file_path}")
        processed_files.add(str(file_path))
        
        # Extract subfolder name
        # The path structure is: /home/website/dynmap_land_claims_extractor/claim_disappearances/[subfolder]/[image]
        # Or directly under claim_disappearances: /home/website/dynmap_land_claims_extractor/claim_disappearances/[image]
        parts = file_path.parts
        base_dir = Path(WATCH_DIR).name
        
        try:
            base_index = parts.index(base_dir)
            if len(parts) > base_index + 2:  # Image is in a subfolder
                subfolder = parts[base_index + 1]
                message = f"New claim disappearance detected in: **{subfolder}**"
            else:  # Image is directly in claim_disappearances
                message = f"New claim disappearance detected in main folder"
                
            # Send to Discord (this will happen in the bot's event loop)
            bot.loop.create_task(send_to_discord(str(file_path), message))
        except Exception as e:
            logger.error(f"Error processing image path: {e}")

async def send_to_discord(file_path, message):
    try:
        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            await channel.send(message, file=discord.File(file_path))
            logger.info(f"Sent image to Discord: {file_path}")
        else:
            logger.error(f"Could not find Discord channel with ID: {DISCORD_CHANNEL_ID}")
    except Exception as e:
        logger.error(f"Error sending to Discord: {e}")

@bot.event
async def on_ready():
    logger.info(f"Bot is ready. Logged in as {bot.user}")
    
def main():
    # Setup watchdog observer
    event_handler = ImageEventHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=True)
    observer.start()
    logger.info(f"Started monitoring {WATCH_DIR}")
    
    try:
        # Get Discord token from environment variable
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            logger.error("DISCORD_TOKEN environment variable not set! Please create a .env file with DISCORD_TOKEN=your_token")
            logger.error(f"Tried looking for .env in current directory and {DEFAULT_ENV_PATH}")
            observer.stop()
            return
            
        # Start the bot
        logger.info("Starting Discord bot...")
        bot.run(token)
    except KeyboardInterrupt:
        logger.info("Stopping due to keyboard interrupt")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        observer.stop()
        observer.join()
        logger.info("Observer stopped")

if __name__ == "__main__":
    main()
