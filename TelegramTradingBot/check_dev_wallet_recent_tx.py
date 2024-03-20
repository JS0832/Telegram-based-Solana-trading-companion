# here I will check the recent activity made by dev .i can simply look at the tx description.
import time

from solana.rpc.api import Client, Pubkey
import helius_api_key
import json
from helius import TransactionsAPI

helius_key = helius_api_key.hel_api_key
URI = "https://mainnet.helius-rpc.com/?api-key=" + str(helius_key)
solana_client = Client(URI)
transactions_api = TransactionsAPI(helius_key)


def check_activity(dev_wallets):
    temp_time_stamp = 9999999999999999999
    temp_description = ""
    for wallet in dev_wallets:
        recent_tx = solana_client.get_signatures_for_address(
            Pubkey.from_string(wallet),
            limit=1  # Specify how much last transactions to fetch
        )
        transaction = json.loads(str(recent_tx.to_json()))["result"]
        parsed_transaction = transactions_api.get_parsed_transactions(transactions=[transaction[0]["signature"]])
        description = parsed_transaction[0]["description"]
        timestamp = parsed_transaction[0]["timestamp"]
        if timestamp < temp_time_stamp:
            temp_time_stamp = timestamp
            temp_description = description
    time_ago = str(int((time.time() - temp_time_stamp) / 60))  # in minutes (60 seconds in a minute
    description_with_link = temp_description.split()
    for index, word in enumerate(description_with_link, start=0):
        if len(word) > 30:  # this is an address
            if word in dev_wallets:
                description_with_link[index] = "Dev Wallet"
            else:
                description_with_link[index] = "Unknown Wallet"
    final_description = " ".join(description_with_link)
    time_string = time_ago + " Minutes Ago"
    return time_string, final_description



