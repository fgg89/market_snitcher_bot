FROM python:3.11.3-bullseye
RUN apt update && apt upgrade -y
RUN apt install -y git rustc
RUN pip install --upgrade pip
RUN git clone https://github.com/fgg89/market_snitcher_bot.git /opt/market_snitcher_bot
RUN cd /opt/market_snitcher_bot && pip install -Ur requirements.txt