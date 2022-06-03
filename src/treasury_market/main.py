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
    tmv, mc = sg.query([last_metric.treasuryMarketValue, last_metric.marketCap])

    return(tmv, mc)


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=300)
async def update_info():
    tmv, mc = get_info()

    if tmv is not None and mc is not None:
        tmv_fmt = f'${prettify_number(tmv)}'
        print(f'TMV: {tmv_fmt}')

        success = await update_nickname(client, f'TMV: {tmv_fmt}')
        if not success:
            return

        success = await update_presence(client, f'TMV/MCap: {tmv/mc:,.2f}')
        if not success:
            return


client.run(BOT_TOKEN)
