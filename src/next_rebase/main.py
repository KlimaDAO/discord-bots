import os
import json
import discord
import requests

from web3 import Web3
from time import time
from discord.ext import commands, tasks
from datetime import datetime, timedelta

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN_REBASE"]
SCAN_API_KEY = os.environ['POLYGONSCAN_API_KEY']

# Initialized Discord client
intents = discord.Intents.default()
intents.members = True  # Subscribe to the privileged members intent.
client = commands.Bot(intents=intents, help_command=None, command_prefix='&?')

# Initialize web3
project_id = os.environ['WEB3_INFURA_PROJECT_ID']
polygon_mainnet_endpoint = f'https://polygon-mainnet.infura.io/v3/{project_id}'
web3 = Web3(Web3.HTTPProvider(
    polygon_mainnet_endpoint,
    request_kwargs={'timeout': 60})
)
assert(web3.isConnected())

address = Web3.toChecksumAddress("0x25d28a24Ceb6F81015bB0b2007D795ACAc411b4d")
abi = json.loads('[{"inputs":[{"internalType":"address","name":"_KLIMA","type":"address"},{"internalType":"address","name":"_sKLIMA","type":"address"},{"internalType":"uint256","name":"_epochLength","type":"uint256"},{"internalType":"uint256","name":"_firstEpochNumber","type":"uint256"},{"internalType":"uint256","name":"_firstEpochBlock","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipPulled","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipPushed","type":"event"},{"inputs":[],"name":"KLIMA","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_recipient","type":"address"}],"name":"claim","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"contractBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"distributor","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"epoch","outputs":[{"internalType":"uint256","name":"length","type":"uint256"},{"internalType":"uint256","name":"number","type":"uint256"},{"internalType":"uint256","name":"endBlock","type":"uint256"},{"internalType":"uint256","name":"distribute","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"forfeit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"giveLockBonus","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"index","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"locker","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"manager","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pullManagement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner_","type":"address"}],"name":"pushManagement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"rebase","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceManagement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"returnLockBonus","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"sKLIMA","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"enum KlimaStaking.CONTRACTS","name":"_contract","type":"uint8"},{"internalType":"address","name":"_address","type":"address"}],"name":"setContract","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_warmupPeriod","type":"uint256"}],"name":"setWarmup","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"address","name":"_recipient","type":"address"}],"name":"stake","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"toggleDepositLock","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"totalBonus","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"bool","name":"_trigger","type":"bool"}],"name":"unstake","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"warmupContract","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"warmupInfo","outputs":[{"internalType":"uint256","name":"deposit","type":"uint256"},{"internalType":"uint256","name":"gons","type":"uint256"},{"internalType":"uint256","name":"expiry","type":"uint256"},{"internalType":"bool","name":"lock","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"warmupPeriod","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]')  # noqa: E501

last_rebase_alert = 0


def get_epoch_info():
    contract_instance = web3.eth.contract(address=address, abi=abi)
    try:
        epoch_info = contract_instance.functions.epoch().call()
    except ValueError:
        epoch_info = None

    return epoch_info


def get_next_rebase_secs(next_rebase_block):
    '''Fetch the block countdown from PolygonScan'''
    resp = requests.get(
        f'https://api.polygonscan.com/api?module=block&action=getblockcountdown&blockno={next_rebase_block}&apikey={SCAN_API_KEY}'  # noqa: E501
    )

    try:
        next_rebase_secs = float(
            json.loads(resp.content)['result']['EstimateTimeInSec']
        )
    except (TypeError, json.decoder.JSONDecodeError):
        next_rebase_secs = None

    return next_rebase_secs


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=60)
async def update_info():
    global last_rebase_alert
    epoch_info = get_epoch_info()

    if epoch_info is None:
        return

    # unpack epoch info
    next_epoch_number = epoch_info[1]
    next_rebase_block = epoch_info[2]

    # Datetime calculations
    next_rebase_secs = get_next_rebase_secs(next_rebase_block)

    if next_rebase_secs is None:
        return

    next_rebase_delta = timedelta(seconds=next_rebase_secs)
    next_rebase_datetime = datetime.utcnow() + next_rebase_delta

    # Extract hours and minutes from timedelta for formatting
    hours, remainder = divmod(next_rebase_delta.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    # Format time
    next_rebase_time = next_rebase_datetime.time().strftime("%H:%M")

    # More than 120s since the last rebase alert
    if next_rebase_secs <= 90 and time() - last_rebase_alert > 120:
        last_rebase_alert = time()
        webhook = discord.Webhook.from_url(
            os.environ["DISCORD_REBASE_BOT_WEBHOOK_URL"],
            adapter=discord.RequestsWebhookAdapter()
        )
        webhook.send(
            "Rebasing momentarily! (:deciduous_tree:, :deciduous_tree:)"
        )

    for guild in client.guilds:
        guser = guild.get_member(client.user.id)
        await guser.edit(nick=f'Rebase In: {int(hours)}h {int(minutes)}m ')

    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=f'Epoch {next_epoch_number} @ {next_rebase_time} UTC'
        )
    )


client.run(BOT_TOKEN)
