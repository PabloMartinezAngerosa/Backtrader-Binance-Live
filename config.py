import os

PRODUCTION = "production"
DEVELOPMENT = "development"

COIN_TARGET = "BTC"
COIN_REFER = "USDT"

ENV = os.getenv("ENVIRONMENT", DEVELOPMENT)
DEBUG = True

# TEST KEY
# API Key: rrkkiKYpKfkk6iM88GEG7k6LlK0VX5a4JjfSKaQQQjCVTtRiB9GNUwWVbHiv0MBf
# Secret Key: YvKlog7B5wlbUIPKLpPT9Aos12S92X0OJfsyCDGythVuN1fbmmNxiQmSNYH3nlgi


# PRODUCTION
 # ExcI0XeCRrWCUfklhGggIFCCNjn9gwB0bsU79qbE0kuASPzrqfOR1BZDhBuJ8lSj 
 # gAPN5Wgv7yeNfxt8eyO8IxmMtyvc235FZsuRngYHek3E5263JqlBs1FtB5xxNQn5
 
BINANCE = {
  "key": "ExcI0XeCRrWCUfklhGggIFCCNjn9gwB0bsU79qbE0kuASPzrqfOR1BZDhBuJ8lSjf",
  "secret": "gAPN5Wgv7yeNfxt8eyO8IxmMtyvc235FZsuRngYHek3E5263JqlBs1FtB5xxNQn5"
}

TELEGRAM = {
  "channel": "<CHANEL ID>",
  "bot": "<BOT KEY HERE>"
}

SQL = {
  "user" : "root",
  "pass" :  "root" 
}

print("ENV = ", ENV)