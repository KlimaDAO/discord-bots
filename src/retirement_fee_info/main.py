import calendar
import os
from datetime import datetime
from discord.ext import tasks

from subgrounds.subgrounds import Subgrounds

from ..constants import KLIMA_CARBON_SUBGRAPH
from ..utils import get_discord_client, \
    update_nickname, update_presence, \
    prettify_number

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
SEVEN_DAYS_IN_SECONDS = 604800

# Initialized Discord client
client = get_discord_client()

sg = Subgrounds()

offsets = ["BCT", "MCO2", "UBO", "NBO", "NCT"]
counter = 0


def get_info():
    global counter
    currentOffset = offsets[counter]

    seven_days_ago_timestamp = get_current_date_timestamp() - SEVEN_DAYS_IN_SECONDS
    weekly_total_fee, weekly_offset_amount, weekly_offset_fee = get_weekly_retirement_fees(sg, seven_days_ago_timestamp, currentOffset)

    counter+=1
    if counter == len(offsets):
        counter=0

    return weekly_total_fee, weekly_offset_amount, weekly_offset_fee, currentOffset


def get_current_date_timestamp():
    date_string = datetime.utcnow().strftime("%d/%m/%Y")
    date = datetime.strptime(date_string, "%d/%m/%Y")
    current_date_timestamp = round(calendar.timegm(date.timetuple()))

    return current_date_timestamp

def get_weekly_retirement_fees(sg, timestamp, offset):
    ''' 
    param `sg`: Initialized subgrounds object
    param `timestamp`: Timestamp used for cutoff date (data created after the provided date will be fetched)
    param `offset`: Specific Offset for which amount and fee will be retrieved

    returns:
    `weekly_total_retirement_fee`: Total fee provided from retirements that were accumulated after the provided timestamp
    `weekly_offset_retirement_amount`: Total amount provided from retirements for specific offset that were accumulated after the provided timestamp
    `weekly_offset_retirement_fee`: Total fee provided from retirements for specific offset that were accumulated after the provided timestamp
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

        weekly_total_retirement_fee = retirement_df["dailyKlimaRetirements_feeAmount"].sum()
        weekly_offset_retirement_amount = retirement_df.loc[retirement_df['dailyKlimaRetirements_token'] == offset,
         'dailyKlimaRetirements_amount'].sum()
        weekly_offset_retirement_fee = retirement_df.loc[retirement_df['dailyKlimaRetirements_token'] == offset,
         'dailyKlimaRetirements_feeAmount'].sum()

        return weekly_total_retirement_fee, weekly_offset_retirement_amount, weekly_offset_retirement_fee

    except Exception as e:
        return None, None, None


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


#Loop time set to 2mins
@tasks.loop(seconds=120)
async def update_info():
    weekly_total_fees, weekly_offset_amount, weekly_offset_fee, offset = get_info()

    if weekly_total_fees is not None and weekly_offset_amount is not None and weekly_offset_fee is not None and offset is not None:

        dao_balance_text = f'Recent KI fees: {prettify_number(weekly_total_fees)}t'
        success = await update_nickname(client, dao_balance_text)
        if not success:
            return

        latest_dao_income_text = f'{offset} retired/fee: {prettify_number(weekly_offset_amount)}t / {prettify_number(weekly_offset_fee)}t'
        success = await update_presence(
            client,
            latest_dao_income_text,
            type='playing'
        )
        if not success:
            return

client.run(BOT_TOKEN)