import os
from telegram.ext import ContextTypes, Application
import yfinance as yf
import logging
import yaml

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = 1733798 
INTERVAL_MIN = 0.05 # minutes

with open('tickers.yaml', "r") as stream:
    try:
        TICKERS = yaml.safe_load(stream)
        logger.info(TICKERS)
    except yaml.YAMLError as exc:
        logger.error(exc)

def get_stock_price(ticker):
    _ticker = yf.Ticker(ticker).info
    logger.debug(_ticker)
    current_price = str(_ticker['currentPrice'])
    return current_price
    
async def callback_scheduled(context: ContextTypes.DEFAULT_TYPE):
    msg = ""
    for ticker in TICKERS['tickers']:
        price = get_stock_price(ticker["name"])
        msg += ticker["name"] + " price: " + price + " " + ticker["currency"] + "\n"
    await context.bot.send_message(chat_id=CHAT_ID, text=msg)

application = Application.builder().token(BOT_TOKEN).build()
job_queue = application.job_queue
job_scheduled = job_queue.run_repeating(callback_scheduled, interval=60*INTERVAL_MIN, first=0)
application.run_polling()