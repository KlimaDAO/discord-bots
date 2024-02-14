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

NOTIFY_ROLE_ID = '912771496122916905'

# Initialized Discord client
client = get_discord_client()

# Initialize web3
web3 = get_polygon_web3()

staking_abi = load_abi('klima_staking.json')

last_warning = 0
last_alert = 0


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


def get_next_rewards_secs(next_rewards_block):
    '''Fetch the block countdown from PolygonScan'''
    resp = requests.get(
        f'https://api.polygonscan.com/api?module=block&action=getblockcountdown&blockno={next_rewards_block}&apikey={SCAN_API_KEY}'  # noqa: E501
    )

    try:
        next_rewards_secs = float(
            json.loads(resp.content)['result']['EstimateTimeInSec']
        )
    except (TypeError, json.decoder.JSONDecodeError):
        next_rewards_secs = None

    return next_rewards_secs


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=60)
async def update_info():
    global last_warning
    global last_alert
    epoch_info = get_epoch_info()

    if epoch_info is None:
        return

    # unpack epoch info
    next_epoch_number = epoch_info[1]
    next_rewards_block = epoch_info[2]

    # Datetime calculations
    next_rewards_secs = get_next_rewards_secs(next_rewards_block)

    if next_rewards_secs is None:
        return

    next_rewards_delta = timedelta(seconds=next_rewards_secs)
    next_rewards_datetime = datetime.utcnow() + next_rewards_delta

    # Extract hours and minutes from timedelta for formatting
    hours, remainder = divmod(next_rewards_delta.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    # Format time
    next_rewards_time = next_rewards_datetime.time().strftime("%H:%M")

    # More than 15m since the last warning
    warning_mins = 15
    warning_secs = warning_mins * 60
    if next_rewards_secs <= warning_secs and time() - last_warning > warning_secs + 30:
        last_warning = time()
        webhook = get_webhook()
        try:
            webhook.send(
                f"Rewards imminent in approximately {warning_mins} minutes <@&{NOTIFY_ROLE_ID}>"
            )
        except discord.errors.NotFound:
            print("Webhook not found")

    # More than 120s since the last alert
    if next_rewards_secs <= 90 and time() - last_alert > 120:
        last_alert = time()
        webhook = get_webhook()
        try:
            webhook.send(
                f"Rewards distributed momentarily! <@&{NOTIFY_ROLE_ID}> (:deciduous_tree:, :deciduous_tree:)"
            )
        except discord.errors.NotFound:
            print("Webhook not found")

    countdown_text = f'Rewards in {int(hours)}h {int(minutes)}m'

    success = await update_nickname(client, countdown_text)
    if not success:
        return

    success = await update_presence(
        client, f'Epoch {next_epoch_number} @ {next_rewards_time} UTC',
        'playing'
    )
    if not success:
        return


client.run(BOT_TOKEN)
