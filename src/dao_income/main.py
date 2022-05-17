import calendar
import os
from datetime import datetime
from discord.ext import tasks

from subgrounds.subgrounds import Subgrounds

from ..constants import KLIMA_ADDRESS, DAO_WALLET_ADDRESS, \
    KLIMA_DECIMALS, KLIMA_BONDS_SUBGRAPH
from ..contract_info import balance_of
from ..utils import get_discord_client, \
    get_polygon_web3, load_abi, \
    update_nickname, update_presence

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

# Initialize web3
web3 = get_polygon_web3()

# Load ABI
erc_20_abi = load_abi('erc20_token.json')

# Initialized Discord client
client = get_discord_client()

sg = Subgrounds()


def get_info():
    dao_balance = get_dao_balance()
    latest_dao_income = get_latest_income()
    return dao_balance, latest_dao_income


def get_dao_balance():
    dao_balance = balance_of(
        web3, KLIMA_ADDRESS, erc_20_abi, KLIMA_DECIMALS, DAO_WALLET_ADDRESS)
    return dao_balance


def get_latest_income():
    '''
    Retrieve latest DAO Wallet income by checking the Daily Bonds Subgraph Query
    '''
    current_date_timestamp = get_current_date_timestamp()
    todays_income = get_todays_dao_income(sg, current_date_timestamp)

    return todays_income


def get_current_date_timestamp():
    date_string = datetime.utcnow().strftime("%d/%m/%Y")
    date = datetime.strptime(date_string, "%d/%m/%Y")
    current_date_timestamp = round(calendar.timegm(date.timetuple()))

    return current_date_timestamp


def get_todays_dao_income(sg, todayts):
    try:
        kbm = sg.load_subgraph(KLIMA_BONDS_SUBGRAPH)

        todays_bonds = kbm.Query.dailyBonds(
            where=[kbm.DailyBond.timestamp == todayts]
        )
        todays_income = sg.query([todays_bonds.daoIncome])

        income_sum = 0
        for income in todays_income:
            income_sum += income

        return income_sum

    except Exception:
        return None


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=300)
async def update_info():
    dao_balance, latest_dao_income = get_info()

    if dao_balance is not None and latest_dao_income is not None:

        dao_balance_text = f'DAO Wallet: {dao_balance:,.2f} KLIMA'
        success = await update_nickname(client, dao_balance_text)
        if not success:
            return

        latest_dao_income_text = f'Today\'s income: {latest_dao_income:,.2f} KLIMA'
        success = await update_presence(
            client,
            latest_dao_income_text,
            type='playing'
        )
        if not success:
            return

client.run(BOT_TOKEN)
