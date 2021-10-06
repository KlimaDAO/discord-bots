import os

import discord
from discord.ext import commands
from discord_slash import SlashCommand  # Importing the newly installed library.
from discord_slash.utils.manage_commands import create_option, create_choice

from guerilla_utils import make_qr_code, overlay_qr, validate_address, STICKER_PATHS

# https://pythondiscord.com/pages/guides/pydis-guides/contributing/setting-test-server-and-bot-account/
token = os.getenv("DISCORD_BOT_TOKEN")

guild_ids = [
    '887786280686075974',  # Personal test server
    # '841390338324824096'  # KlimaDAO official community server
]

# TODO: create dedicated channel and limit Slash commands to that channel

bot = commands.Bot('.', intents=discord.Intents.default())
slash = SlashCommand(bot, sync_commands=True)  # Declares slash commands through the client.


@bot.event
async def on_ready():
    print("Ready!")


@slash.subcommand(base="guerilla",
                  name="menu",
                  description="Show the menu of memes to accompany guerilla marketing QR codes.")
async def guerilla_menu(ctx):
    await ctx.send("Here be 🌳 memes", files=[discord.File(path) for path in STICKER_PATHS.values()])


@slash.subcommand(base="guerilla",
                  name="request",
                  description="Request a customized guerilla marketing sticker with unique QR code.",
                  options=[
                    create_option(
                     name="location",
                     description="City or country for tracking by location.",
                     option_type=3,
                     required=True
                    ),
                    create_option(
                     name="address",
                     description="Public address of your Ethereum wallet with non-zero aKLIMA balance.",
                     option_type=3,
                     required=True
                    ),
                    create_option(
                     name="sticker_id",
                     description="Choose which sticker image you would like to accompany your QR code.",
                     option_type=3,
                     required=True,
                     choices=[
                       create_choice(
                         name="Carbon Guzzler",
                         value='carbonguzzler'
                       ),
                       create_choice(
                         name="Virgin vs. Chad",
                         value='virginchad'
                       )
                     ]
                    ),
                  ])
async def guerilla_request(ctx, location, address, sticker_id):
    await ctx.defer()

    is_valid = validate_address(address)
    if not is_valid:
        await ctx.send(
            "Invalid address provided - please confirm that it is a "
            "valid ETH mainnet address and has a non-zero aKLIMA balance"
        )
        return

    qr_img = make_qr_code(location, address, sticker_id)

    custom_img_path = f'./custom_qr_{location}_{address}_{sticker_id}.png'
    overlay_qr(qr_img, sticker_id, custom_img_path)

    await ctx.send(
      "Here's your guerilla marketing sticker with personalized QR code! Print some out and go paint the town 🌳",
      file=discord.File(custom_img_path),
      # hidden=True
    )

    # TODO: Clean up generated image files


bot.run(token)
