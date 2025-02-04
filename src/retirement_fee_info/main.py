import os
from discord.ext import tasks
from web3 import Web3

from subgrounds.subgrounds import Subgrounds

from ..time_utils import get_days_ago_timestamp

from ..constants import POLYGON_DIGITAL_CARBON_SUBGRAPH, \
    BCT_ADDRESS, UBO_ADDRESS, NBO_ADDRESS, MCO2_ADDRESS, NCT_ADDRESS

from ..utils import get_discord_client, \
    update_nickname, update_presence, \
    prettify_number

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

# Initialized Discord client
client = get_discord_client()

sg = Subgrounds()

pool_names = ["BCT", "MCO2", "UBO", "NBO", "NCT"]
pool_addresses = {
    'BCT': BCT_ADDRESS,
    'NBO': NBO_ADDRESS,
    'UBO': UBO_ADDRESS,
    'NCT': NCT_ADDRESS,
    'MCO2': MCO2_ADDRESS
}
counter = 0


def get_info():
    global counter
    current_pool = pool_names[counter]

    ts = get_days_ago_timestamp(7)
    w_retired_amount = get_retirement_fees(sg, ts, current_pool)

    counter += 1
    if counter == len(pool_names):
        counter = 0

    return w_retired_amount, current_pool


def get_retirement_fees(sg, timestamp, pool):
    '''
    param `sg`: Initialized subgrounds object
    param `timestamp`: Timestamp used for cutoff date (data created after
    the provided date will be fetched)
    param `pool`: Specific pool for which amount and fee will be retrieved

    returns:
    `w_pool_amount`: Total amount provided from retirements
    '''

    try:
        pdc = sg.load_subgraph(POLYGON_DIGITAL_CARBON_SUBGRAPH)

        retirement_df = pdc.Query.dailyKlimaRetireSnapshots(
            where=[pdc.Query.dailyKlimaRetireSnapshots.timestamp > timestamp]
        )

        retirement_df = sg.query_df(
            [retirement_df.amount,
             retirement_df.feeAmount,
             retirement_df.pool])

        if retirement_df.size == 0:
            return 0, 0, 0

        retirement_df['dailyKlimaRetireSnapshots_pool'] = retirement_df.dailyKlimaRetireSnapshots_pool.apply(
            lambda x: Web3.to_checksum_address(x)
        )

        w_pool_amount = retirement_df.loc[
            retirement_df['dailyKlimaRetireSnapshots_pool'] == pool_addresses[pool],
            'dailyKlimaRetireSnapshots_amount'
        ].sum()

        return w_pool_amount

    # TODO: clean up this bad practice and add better monitoring for bots going down
    except Exception as e:
        print(e)
        return None


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


# Loop time set to 2mins
@tasks.loop(seconds=120)
async def update_info():
    pool_amount, pool = get_info()

    if pool_amount and pool is not None:

        pool_text = f'Retired {pool}: {prettify_number(pool_amount)}t'
        success = await update_nickname(client, pool_text)
        if not success:
            return

        total_text = 'in the last 7d'
        success = await update_presence(
            client,
            total_text,
            type='playing'
        )
        if not success:
            return

client.run(BOT_TOKEN)
