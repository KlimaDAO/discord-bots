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

## Deployment

The bots are hosted as separate applications on Digital Ocean App Platform. Upon any commit to the `master` branch, the bots are deployed automatically.

The `Dockerfile` is used to provide a base environment for build and deployment.

### Required Environment

The following environment variables must be defined in the DOAP setup:

BCT Price:

- `DISCORD_BOT_TOKEN`
- `WEB3_INFURA_PROJECT_ID`

Guerilla Marketing:

- `DISCORD_BOT_TOKEN`

KLIMA Price:

- `DISCORD_BOT_TOKEN`
- `WEB3_INFURA_PROJECT_ID`

Next Rebase:

- `DISCORD_BOT_TOKEN_REBASE`
- `POLYGONSCAN_API_KEY`
- `WEB3_INFURA_PROJECT_ID`
