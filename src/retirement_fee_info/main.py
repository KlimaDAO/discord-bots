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


def get_weekly_retirement_fees(sg, seven_days_ago_timestamp, offset):
    try:
        kbm = sg.load_subgraph(KLIMA_CARBON_SUBGRAPH)

        weekly_retirement_response = kbm.Query.dailyKlimaRetirements(
            where=[kbm.DailyKlimaRetirement.timestamp > seven_days_ago_timestamp]
        )
        weekly_retirement_response = sg.query_json([weekly_retirement_response.token, weekly_retirement_response.amount, weekly_retirement_response.feeAmount, ])
        
        #We know that there will be one item in dictionary which represents a response
        #Therefore we get the first key in the dictionary and get response via that key
        #Its easier to iterate through response this way compared to "query" method
        key = list(weekly_retirement_response[0].keys())[0]
        weekly_retirements = weekly_retirement_response[0][key]

        weekly_total_retirement_fee = 0

        weekly_offset_retirement_amount = 0
        weekly_offset_retirement_fee = 0
        for retirement in weekly_retirements:
            weekly_total_retirement_fee += retirement["feeAmount"]
            if offset == retirement["token"]:
                weekly_offset_retirement_amount += retirement["amount"]
                weekly_offset_retirement_fee += retirement["feeAmount"]

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