from datetime import datetime, timedelta
import os
import json
from time import time

import discord
from discord.ext import tasks
import requests

from ..constants import STAKING_ADDRESS
from ..utils import get_discord_client, get_polygon_web3, load_abi, update_nickname, update_presence


BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
SCAN_API_KEY = os.environ['POLYGONSCAN_API_KEY']

REBASER_ROLE_ID = '912771496122916905'

# Initialized Discord client
client = get_discord_client()

# Initialize web3
web3 = get_polygon_web3()

staking_abi = load_abi('klima_staking.json')

last_rebase_warning = 0
last_rebase_alert = 0


def get_webhook():
    return discord.SyncWebhook.from_url(
        os.environ["DISCORD_REBASE_BOT_WEBHOOK_URL"]
    )


def get_epoch_info():
    contract_instance = web3.eth.contract(address=STAKING_ADDRESS, abi=staking_abi)
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
    global last_rebase_warning
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

    # More than 15m since the last rebase warning
    warning_mins = 15
    warning_secs = warning_mins * 60
    if next_rebase_secs <= warning_secs and time() - last_rebase_warning > warning_secs + 30:
        last_rebase_warning = time()
        webhook = get_webhook()
        try:
            webhook.send(
                f"Rebase imminent in approximately {warning_mins} minutes <@&{REBASER_ROLE_ID}>"
            )
        except discord.errors.NotFound:
            print("Webhook not found")

    # More than 120s since the last rebase alert
    if next_rebase_secs <= 90 and time() - last_rebase_alert > 120:
        last_rebase_alert = time()
        webhook = get_webhook()
        try:
            webhook.send(
                f"Rebasing momentarily! <@&{REBASER_ROLE_ID}> (:deciduous_tree:, :deciduous_tree:)"
            )
        except discord.errors.NotFound:
            print("Webhook not found")

    countdown_text = f'Rebase In: {int(hours)}h {int(minutes)}m'

    success = await update_nickname(client, countdown_text)
    if not success:
        return

    success = await update_presence(
        client, f'Epoch {next_epoch_number} @ {next_rebase_time} UTC',
        'playing'
    )
    if not success:
        return


client.run(BOT_TOKEN)
