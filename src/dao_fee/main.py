import os
from discord.ext import tasks

from subgrounds.subgrounds import Subgrounds

from ..constants import KLIMA_BONDS_SUBGRAPH
from ..utils import get_discord_client, \
    prettify_number, \
    update_nickname, update_presence
from ..time_utils import get_days_ago_timestamp

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

# Initialized Discord client
client = get_discord_client()

sg = Subgrounds()


def get_info():
    latest_dao_fee = get_latest_fee()
    return latest_dao_fee


def get_latest_fee():
    '''
    Retrieve recent DAO Wallet fee by checking the Daily Bonds Subgraph Query
    '''
    ts = get_days_ago_timestamp(7)
    todays_fee = get_recent_dao_fee(sg, ts)

    return todays_fee


def get_recent_dao_fee(sg, ts):
    try:
        kbm = sg.load_subgraph(KLIMA_BONDS_SUBGRAPH)

        weekly_bonds = kbm.Query.dailyBonds(
            where=[kbm.DailyBond.timestamp > ts]
        )

        fee_df = sg.query_df([weekly_bonds.daoFee])
        todays_fees = fee_df["dailyBonds_daoFee"].sum()

        return todays_fees

    except Exception:
        return None


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=300)
async def update_info():
    latest_dao_fee = get_info()

    if latest_dao_fee is not None:
        fee_text = f'Fees: {prettify_number(latest_dao_fee)} KLIMA'

        presence_text = "from the last 7d bonds"
        success = await update_nickname(client, fee_text)
        if not success:
            return

        success = await update_presence(
            client,
            presence_text,
            type='playing'
        )
        if not success:
            return

client.run(BOT_TOKEN)
