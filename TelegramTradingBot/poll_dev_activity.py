import time
from telebot.async_telebot import AsyncTeleBot
from solana.rpc.api import Client, Pubkey
import helius_api_key
import json
from helius import TransactionsAPI


helius_key = helius_api_key.hel_api_key
URI = "https://mainnet.helius-rpc.com/?api-key=" + str(helius_key)
solana_client = Client(URI)
transactions_api = TransactionsAPI(helius_key)
TOKEN = "6769248171:AAERXN-athfaM8JtK7kTYfNO6IpfJav7Iug"
bot = AsyncTeleBot(token=TOKEN)


async def poll_activity(dev_wallets, user_id):
    disable = False
    tx_hash_wallets = []
    for wallet in dev_wallets:
        recent_tx = solana_client.get_signatures_for_address(
            Pubkey.from_string(wallet),
            limit=1  # Specify how much last transactions to fetch
        )
        transaction = json.loads(str(recent_tx.to_json()))["result"]
        tx_hash_wallets.append(transaction[0]["signature"])
    start_time = time.time()
    while not disable:
        for wallet in dev_wallets:
            recent_tx = solana_client.get_signatures_for_address(
                Pubkey.from_string(wallet),
                limit=1  # Specify how much last transactions to fetch
            )
            transaction = json.loads(str(recent_tx.to_json()))["result"]
            if transaction not in tx_hash_wallets:
                parsed_transaction = transactions_api.get_parsed_transactions(
                    transactions=[transaction[0]["signature"]])
                description = parsed_transaction[0]["description"]
                await bot.send_message(user_id, "INFO! " + str(description))
                # send ms add tx t the wallet
                tx_hash_wallets.append(transaction)
        time.sleep(1)
        if start_time + 600 > time.time():
            await bot.send_message(user_id, "Polling has been turned ,press again to continue listening ")
            return
    return  # closing thread
