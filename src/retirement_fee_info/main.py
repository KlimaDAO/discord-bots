import os
from discord.ext import tasks

from subgrounds.subgrounds import Subgrounds

from ..time_utils import get_days_ago_timestamp

from ..constants import KLIMA_CARBON_SUBGRAPH
from ..utils import get_discord_client, \
    update_nickname, update_presence, \
    prettify_number

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

# Initialized Discord client
client = get_discord_client()

sg = Subgrounds()

offsets = ["BCT", "MCO2", "UBO", "NBO", "NCT"]
counter = 0


def get_info():
    global counter
    currentOffset = offsets[counter]

    ts = get_days_ago_timestamp(7)
    w_offset_amount = get_retirement_fees(sg,
                                          ts,
                                          currentOffset)

    counter += 1
    if counter == len(offsets):
        counter = 0

    return w_offset_amount, currentOffset


def get_retirement_fees(sg, timestamp, offset):
    '''
    param `sg`: Initialized subgrounds object
    param `timestamp`: Timestamp used for cutoff date (data created after
    the provided date will be fetched)
    param `offset`: Specific Offset for which amount and fee will be retrieved

    returns:
    `w_offset_amount`: Total amount provided from retirements
    '''

    try:
        kbm = sg.load_subgraph(KLIMA_CARBON_SUBGRAPH)

        retirement_df = kbm.Query.dailyKlimaRetirements(
            where=[kbm.DailyKlimaRetirement.timestamp > timestamp]
        )

        retirement_df = sg.query_df(
            [retirement_df.amount,
             retirement_df.feeAmount,
             retirement_df.token])

        if retirement_df.size == 0:
            return 0, 0, 0

        w_offset_amount = retirement_df.loc[
            retirement_df['dailyKlimaRetirements_token'] == offset,
            'dailyKlimaRetirements_amount'].sum()

        return w_offset_amount

    except Exception:
        return None


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


# Loop time set to 2mins
@tasks.loop(seconds=120)
async def update_info():
    offset_amount, offset = get_info()

    if offset_amount and offset is not None:

        offset_text = f'Retired {offset}: {prettify_number(offset_amount)}t'
        success = await update_nickname(client, offset_text)
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
