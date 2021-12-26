# discord-bots

Custom Discord Bots powering the KlimaDAO community.

This is a monorepo containing multiple bots:

- BCT price:
- Guerilla marketing:
- KLIMA price:
- Next rebase:

## Layout

src/

- bct_price/
- guerilla_marketing/
- klima_price/
- next_rebase/

## Setup

Each bot requires a separate application to be defined in the Discord Developer Portal. For each, do the following:

1. Access the Discord developer portal: <https://discord.com/developers/applications>
1. Create a new application: enter in the name of the bot (e.g. next-rebase)
1. Create a bot: Click on "bot" in the sidebar and define a bot with the corresponding username.
   1. Check the "presence" and "server members" intents.
1. Authorise the bot:
   1. Click on OAuth2 -> URL Generator in the sidebar.
   1. Select the "bot" scope.
   1. Copy the generated URL and open it.
   1. Select your server from the list and click on "Authorize". (You'll know that this has worked, as the bot user will appear in your Discord server.)
1. Obtain the token for the bot: Settings -> Bot -> Token -> Copy

## API Keys

This project requires some API keys to run. When developing locally, you can create your own API keys from the following services:

- Infura: create a new project - <https://infura.io/dashboard>
  - Note that you need to enable the Polygon add-on: <https://infura.io/payment?chosenAddon=ethereum_polygon_addon>
- PolygonScan: create an account - <https://polygonscan.com/myapikey>
- Discord webhook URL: create a personal server, channel settings -> integrations, create webhook

## Deployment

The bots are hosted on Digital Ocean App Platform under a single app. Upon any commit to the `master` branch, the bots are deployed automatically.

Deployment follows this process:

- A Docker image is built and pushed to DOCR using the `Dockerfile`.
  - Note: This Docker image contains the source code to the bots. Do **NOT** include any confidential or proprietary information in the repository or build artifacts.
- The app is deployed to Digital Ocean, using the built Docker image as the basis.

### Required Environment

The following environment variables must be defined in the Digital Ocean App Platform environment:

App-level:

- `WEB3_INFURA_PROJECT_ID`
- `POLYGONSCAN_API_KEY`

Component-level (app -> settings -> components):

BCT Price:

- `DISCORD_BOT_TOKEN`

Guerilla Marketing:

- `DISCORD_BOT_TOKEN`

KLIMA Price:

- `DISCORD_BOT_TOKEN`

Next Rebase:

- `DISCORD_BOT_TOKEN_REBASE`
- `DISCORD_REBASE_BOT_WEBHOOK_URL`
