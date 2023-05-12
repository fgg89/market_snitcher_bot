export BOT_TOKEN=$(cat bot_token.txt)

https://schedule.readthedocs.io/en/stable/examples.html

https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions---JobQueue

pip install python-telegram-bot[job-queue]

docker network create market_snitcher

Run locally:

export BOT_TOKEN=$(cat .env | grep BOT_TOKEN | awk -F'=' '{print $2}')
export CHAT_ID=$(cat .env | grep CHAT_ID | awk -F'=' '{print $2}')
export INTERVAL_MIN=$(cat .env | grep INTERVAL_MIN | awk -F'=' '{print $2}')
export TICKERS_FILE=$(cat .env | grep TICKERS_FILE | awk -F'=' '{print $2}')
