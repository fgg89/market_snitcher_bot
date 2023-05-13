import os
from telegram.ext import ContextTypes, Application
import yfinance as yf
import logging
import yaml
from currency_converter import CurrencyConverter
import requests

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
INTERVAL_MIN = float(os.environ.get("INTERVAL_MIN"))
TICKERS_FILE = os.environ.get("TICKERS_FILE")
ECB_URL = "http://www.ecb.europa.eu/stats/eurofxref/eurofxref.zip"
SAVE_PATH = "./eurofxref.zip"

with open(TICKERS_FILE, "r") as stream:
    try:
        TICKERS = yaml.safe_load(stream)
        logger.debug(TICKERS)
    except yaml.YAMLError as exc:
        logger.error(exc)


def get_stock_price(ticker):
    _ticker = yf.Ticker(ticker).info
    logger.debug(_ticker)
    current_price = _ticker["currentPrice"]
    return round(current_price, 2)


def get_exchange_rates(url, save_path, chunk_size=128):
    r = requests.get(url, stream=True)
    with open(save_path, "wb") as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)


async def callback_scheduled(context: ContextTypes.DEFAULT_TYPE):
    msg = ""
    nav_today = 0
    # Get the latest exchange rate
    get_exchange_rates(ECB_URL, SAVE_PATH)
    # Create the currency converter
    converter = CurrencyConverter(ECB_URL)
    for index, ticker in enumerate(TICKERS["tickers"]):
        if ticker["currency"] == "EUR":
            current_price = get_stock_price(ticker["name"])
            current_price_eur = current_price
        elif ticker["currency"] == "GBP":
            current_price = get_stock_price(ticker["name"]) / 100
            current_price_eur = converter.convert(
                (get_stock_price(ticker["name"])) / 100, "GBP", "EUR"
            )
        else:
            current_price = get_stock_price(ticker["name"])
            current_price_eur = converter.convert(
                (get_stock_price(ticker["name"])), ticker["currency"], "EUR"
            )
        delta = current_price - ticker["buy_price"]
        diff = round((delta / ticker["buy_price"]) * 100, 2)
        msg += (
            "<code>"
            + ticker["name"]
            + "</code>"
            + " | "
            + str(round(current_price, 2))
            + " "
            + ticker["currency"]
            + " | "
            + "<b>"
            + str(round(diff, 2))
            + "</b>"
            + " %"
            + "\n"
        )
        stock_value = round(ticker["shares"] * current_price_eur, 2)
        nav_today += stock_value
        # Print NAV when after reaching the last item in the list
        if index == len(TICKERS["tickers"]) - 1:
            msg += "\n" + "<b>" + "NAV" + "</b>: " + str(nav_today) + " EUR"
    await context.bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")


application = Application.builder().token(BOT_TOKEN).build()
job_queue = application.job_queue
job_scheduled = job_queue.run_repeating(
    callback_scheduled, interval=60 * INTERVAL_MIN, first=0
)
application.run_polling()
