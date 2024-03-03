import time
import telegram
import asyncio

token = ["ererggegergeg"]


def main():
    i = 0
    for x in range(10):
        send_to_telegram(
            "💸  Market Cap detected- \n 🎉  Initial Liquidity- \n 🔥  Liquidity Burned- \n 🌊  "
            "Tokens sent to"
            "LP- \n 💳  Wallet Distribution- \n 📝  Metadata Match- \n\n  "
            "📈  Chart- " + f"https://dexscreener.com"
                           f"/solana/{token[0]}")

        i += 1


def send_to_telegram(new_token_address):

    try:
        bot = telegram.Bot(token='6405793513:AAEPOCPP022SkJlg6iYI-RgSHJ9AZOaoQy4')
        asyncio.run(bot.sendMessage(chat_id="-4129157033", text=" Found a new coin: \n\n " + new_token_address))
        bot = telegram.Bot(token='6405793513:AAEPOCPP022SkJlg6iYI-RgSHJ9AZOaoQy4')
        asyncio.run(bot.sendMessage(chat_id="-4129157033",
                                                                                      text="🎉  Initial Liquidity-" + str(
                                                                                          token[6]) + " \n 🔥  "
                                                                                                      "Liquidity Burned- " + " \n 🌊"
                                                                                                        "Tokens sent to"
                                                                                                        "LP- " + " \n 💳  decentralisation - " + " \n 💳  number of top ten  - "
                                                                                           + " \n Dev Sniper Free? "
                                                                                                               "- yes \n top holder cumulative total: " +

                                                                                           "\n\n 📈  Chart- " + f"https"
                                                                                                               f"://dexscreener.com"
                                                                                                               f"/solana/{token[0]} \n  checked on time?: " ))
    except Exception as e:
        print("Unable to send: ", e)
    time.sleep(3)


if __name__ == "__main__":
    main()
