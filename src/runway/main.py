from datetime import datetime, timezone
import os
from discord.ext import tasks

from subgrounds.subgrounds import Subgrounds

from ..utils import get_discord_client, \
                    update_nickname, update_presence, get_last_metric

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

# Initialized Discord client
client = get_discord_client()

sg = Subgrounds()
def get_runway():
     last_metric = get_last_metric(sg)

     runway =  sg.query([last_metric.runwayCurrent])
     timestamp =  sg.query([last_metric.timestamp])

     return runway, timestamp

def get_info():
     runway, timestamp = get_runway()

     return runway, timestamp

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=300)
async def update_info():
    runway, timestamp = get_info()

    if runway is not None and timestamp is not None:

        runway_rounded = round(runway)
        success = await update_nickname(client, f'Runway: {runway_rounded} days')
        if not success:
            return

        dt_ts = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        formatted_timestamp = dt_ts.strftime("%Y-%m-%d %H:%M:%S")
        success = await update_presence(client, f'Last checked: {formatted_timestamp}')
        if not success:
            return

client.run(BOT_TOKEN)