import os
from telegram.ext import ContextTypes, Application
import yfinance as yf
import logging
import yaml
from currency_converter import CurrencyConverter
import requests
from datetime import datetime
import pytz


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
INTERVAL_MIN = float(os.environ.get("INTERVAL_MIN", 0.15))
DATA_FILE = os.environ.get("DATA_FILE", "data.yaml")
START_TIME = os.environ.get("START_TIME", "09:00")
END_TIME = os.environ.get("END_TIME", "20:00")
LIMIT_WEEKDAY = os.environ.get("LIMIT_WEEKDAY", 7)
ECB_URL = "http://www.ecb.europa.eu/stats/eurofxref/eurofxref.zip"
SAVE_PATH = "./eurofxref.zip"

with open(DATA_FILE, "r") as stream:
    try:
        DATA = yaml.safe_load(stream)
        logger.debug(DATA)
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
    # Get the current CEST time
    # TODO: Make the timezone configurable
    tz = pytz.timezone("Europe/Madrid")
    current_time = datetime.now(tz).time()
    # Check if the current day is Monday to Friday (0-4) and the current time is between 9 AM and 6 PM
    if (
        datetime.today().weekday() < LIMIT_WEEKDAY
        and current_time >= datetime.strptime(START_TIME, "%H:%M").time()
        and current_time <= datetime.strptime(END_TIME, "%H:%M").time()
    ):
        msg = ""
        nav_today = 0
        # Get the latest exchange rate
        get_exchange_rates(ECB_URL, SAVE_PATH)
        # Create the currency converter
        converter = CurrencyConverter(ECB_URL)
        for index, ticker in enumerate(DATA["stocks"]):
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
            stock_value = ticker["shares"] * current_price_eur
            nav_today += stock_value
            total_stocks_invested = DATA["total_stocks_invested"]
            twr_rate = ((nav_today - total_stocks_invested)/total_stocks_invested)*100
            # twr = nav_today - total_stocks_invested
            # forex = round(((DATA["forex"]["value"] - DATA["forex"]["cost_basis"])/DATA["forex"]["cost_basis"])*100, 2)
            # forex = DATA["forex"]["value"] - DATA["forex"]["cost_basis"]
            # Print total values of interest after reaching the last item in the list
            if index == len(DATA["stocks"]) - 1:
                msg += "\n" + "<b>" + "NAV" + "</b>: " + str(round(nav_today,2)) + " EUR"
                msg += "\n" + "<b>" + "TWR" + "</b>: " + str(round(twr_rate,2)) + " %"

        await context.bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")


application = Application.builder().token(BOT_TOKEN).build()
job_queue = application.job_queue
job_repeating = job_queue.run_repeating(
    callback_scheduled, interval=60 * INTERVAL_MIN, first=0
)
application.run_polling()
