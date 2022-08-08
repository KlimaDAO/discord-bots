import os

from discord.ext import tasks

from subgrounds.subgrounds import Subgrounds

from ..utils import get_discord_client, prettify_number, \
    update_nickname, update_presence, \
    get_last_metric

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

# Initialized Discord client
client = get_discord_client()

sg = Subgrounds()


def get_info():
    last_metric = get_last_metric(sg)
    total_cc, total_carbon = sg.query([last_metric.treasuryCarbonCustodied, last_metric.treasuryCarbon])

    return total_cc, total_carbon


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=300)
async def update_info():
    cc, total_carbon = get_info()

    if cc is not None and total_carbon is not None:
        total_fmt = f'{prettify_number(total_carbon)}t'
        print(f'TTC: {total_fmt}')

        success = await update_nickname(client, f'TTC: {total_fmt}')
        if not success:
            return

        success = await update_presence(client, f'Total CC: {cc/1e6:,.1f}Mt')
        if not success:
            return


client.run(BOT_TOKEN)
