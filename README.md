# discord-bots

Custom Discord Bots powering the KlimaDAO community.

This is a monorepo containing multiple bots.

## Layout

src/

- each folder corresponds to a specific bot

## Setup

Each bot requires a separate application to be defined in the Discord Developer Portal. For each, do the following:

1. Access the Discord developer portal: <https://discord.com/developers/applications>
1. Create a new application: enter in the name of the bot (e.g. next-rewards)
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

The bots are hosted on Digital Ocean App Platform under a single app. Upon any commit to the `main` or `staging` branches, the bots are deployed automatically.

Before this, the app must be created. It can be done through the DigitalOcean App Platform web interface, or through the `make create` command.

Deployment follows this process:

- A Docker image is built and pushed to DOCR using the `Dockerfile`.
  - Note: This Docker image contains the source code to the bots. Do **NOT** include any confidential or proprietary information in the repository or build artifacts.
- The app is deployed to Digital Ocean, using the built Docker image as the basis.

To deploy manually, run:

`DIGITALOCEAN_APP_ID=<INSERT ID> DIGITALOCEAN_ACCESS_TOKEN=<INSERT TOKEN> make deploy`

### Required Environment

#### GitHub Actions

The following environment variables must be defined in GitHub Actions:

- `DIGITALOCEAN_ACCESS_TOKEN`
  - Generate a personal access token at the following URL: <https://cloud.digitalocean.com/account/api/tokens>
- `DIGITALOCEAN_APP_NAME`
- `DIGITALOCEAN_APP_ID`
  - In the Digital Ocean web interface, go to project -> apps, and copy the ID from the URL, e.g. `SOME-222-random-string` in <https://cloud.digitalocean.com/apps/SOME-222-random-string/settings>
- `DIGITALOCEAN_CONTAINER_REPO`
  - Name of the Docker image registry hosted by Digital Ocean. It will be the name listed on this page: <https://cloud.digitalocean.com/registry>

These variables must also be defined, and will be used to replace variables in the app-spec.yml file:

- `POLYGONSCAN_API_KEY`
- `WEB3_PROVIDER_ETH_URL`
- `WEB3_PROVIDER_POLYGON_URL`
- `DISCORD_BOT_TOKEN_KLIMA_PRICE`
- `DISCORD_BOT_TOKEN_BCT_PRICE`
- `DISCORD_BOT_TOKEN_MCO2_PRICE`
- `DISCORD_BOT_TOKEN_STAKING_REWARDS`
- `DISCORD_BOT_TOKEN_CCO2_PRICE`
- `DISCORD_BOT_TOKEN_MANIC_PRICE`
- `DISCORD_BOT_TOKEN_WOOD_PRICE`


**NOTE: in order for environment variables defined as GitHub Actions Secrets/Variables to be propagated properly from GitHub Actions into the deployed Docker containers, they must be mapped in several places:**
1. Into the build environment via the `.github/workflows/deploy.yaml` file `env` section of the `Deploy` step
1. Into the k8s build via `k8s/secret.properties.template`
1. Into the actual k8s secret via `k8s/base/deployment.yaml` or the corresponding bot-specific `deployment_set_<bot_name>.yaml` file in the appropriate bot-specific directory under `k8s`


#### Digital Ocean App Platform

The above environment variables are used in the Digital Ocean App Platform environment. They are injected into the `app-spec.yml` file for the following reasons:

- It is cumbersome to include the secret in the configuration file, deploy it and then copy/paste the encrypted value into the file again.
- Updating secrets becomes cumbersome as well.

Instead, it is much easier to define and rotate secrets through the GitHub Actions secrets. We use the `envsubst` tool to achieve this.

### Multiple Deployments

Each Docker image is tagged with the GitHub commit SHA, which prevents parallel deployments (`main` and `staging`) from clobbering each other.

In order for parallel deployments to work, however, the following must be implemented:

- Define the "default" (non-production) environment variables for the GitHub repository. This ensures that any new branches will use non-production variables by default.
- Create an environment called "main" and define any variables that _differ_ from the default variables. At a minimum, this should include:
  - `DIGITALOCEAN_APP_ID` (or else different branches will be the same DigitalOcean app and clobber each other).
  - All of the `DISCORD_BOT_*` tokens (or else those bots will be clobbered).
