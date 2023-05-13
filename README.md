# README

## Links

* https://schedule.readthedocs.io/en/stable/examples.html
* https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions---JobQueue
* http://alexprengere.github.io/currencyconverter/

## How to run

Create a ``.env`` file with the following content and place it at the root of the repository:

```
BOT_TOKEN=<YOUR_BOT_TOKEN>
CHAT_ID=<YOUR_CHAT_ID>
INTERVAL_MIN=5
TICKERS_FILE=tickers.yaml
```

### Using docker-compose

Create the docker network (once only):

```
docker network create market_snitcher
```

```
docker-compose --env-file .env up -d
```

### Locally

```
python3 -m venv .venv
source .venv/bin/activate
pip install -Ur requirements.txt
```

```
export BOT_TOKEN=$(cat .env | grep BOT_TOKEN | awk -F'=' '{print $2}')
export CHAT_ID=$(cat .env | grep CHAT_ID | awk -F'=' '{print $2}')
export INTERVAL_MIN=$(cat .env | grep INTERVAL_MIN | awk -F'=' '{print $2}')
export TICKERS_FILE=$(cat .env | grep TICKERS_FILE | awk -F'=' '{print $2}')
```

```
python bot.py
```