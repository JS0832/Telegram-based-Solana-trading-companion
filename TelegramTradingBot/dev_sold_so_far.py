# here calculate if the dev sold anything so far and add their wallets for polling later
from requests import request
import time
from requests import request
from helius import TransactionsAPI
from helius import BalancesAPI
import json
from solana.rpc.api import Client, Pubkey

solscan_header = {
    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MDY3NTM5ODAzOTQsImVtYWlsIjoic29sYmFieTMyNUBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJpYXQiOjE3MDY3NTM5ODB9.Lp77APFLV-rOnNbDzc1ob43Vp-9-KpeMe_b-fiOQrr0',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.82 Safari/537.36'
}
transactions_api = TransactionsAPI("3e1717e1-bf69-45ae-af63-361e43b78961")
balances_api = BalancesAPI("3e1717e1-bf69-45ae-af63-361e43b78961")


def check_dev(txn_hash, token_d):  # instead of recomputing how about tracking the wallets
    liquidity_tx_info = request('GET',
                                "https://pro-api.solscan.io/v1.0/transaction/" + str(
                                    txn_hash),
                                headers=solscan_header)

    liquidity_tx_info_json = liquidity_tx_info.json()
    signer = str(liquidity_tx_info_json["signer"][0])
    token_address = token_d
    URI = "https://mainnet.helius-rpc.com/?api-key=3e1717e1-bf69-45ae-af63-361e43b78961"
    solana_client = Client(URI)
    all_seen_wallets = []
    temp_associated_wallets = []  # (stack) for all associated wallets
    root = signer
    if root == "":
        return "error"
    temp_associated_wallets.append(root)
    all_seen_wallets.append(root)
    total_sold = 0
    while True:  # here traverse all wallets connected to one wallet and count the total supply holding.
        if len(temp_associated_wallets) > 0:  # means there is more to check
            temp_wallet = str(temp_associated_wallets.pop())
            print("checking " + str(temp_wallet))
            res = solana_client.get_signatures_for_address(
                Pubkey.from_string(temp_wallet),
                limit=30  # Specify how much last transactions to fetch
            )
            transactions = json.loads(str(res.to_json()))["result"]
            for tx_hash in transactions:  # loop over all transaction per give wallet (limit it to 20)
                parsed_transactions = transactions_api.get_parsed_transactions(transactions=[tx_hash["signature"]])
                if len(parsed_transactions[0]["tokenTransfers"]) > 0:
                    for tx_items in parsed_transactions[0]["tokenTransfers"]:
                        if str(tx_items["mint"]) == token_address:
                            if str(tx_items["toUserAccount"]) == temp_wallet:
                                if str(tx_items[
                                           "fromUserAccount"]) != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1" and str(
                                    tx_items[
                                        "fromUserAccount"]) != "":  # because that's just a mint operation and
                                    # the dev buying which is fine
                                    temp_associated_wallets.append(str(tx_items["fromUserAccount"]))
                                    all_seen_wallets.append(str(tx_items["fromUserAccount"]))
                            elif str(tx_items["fromUserAccount"]) == temp_wallet:
                                if str(tx_items["toUserAccount"]) != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":
                                    print("sent to wallet " + str(tx_items["toUserAccount"]))
                                    temp_associated_wallets.append(str(tx_items["toUserAccount"]))
                                    all_seen_wallets.append(str(tx_items["toUserAccount"]))
                                else:
                                    total_sold += tx_items["tokenAmount"]
        print(temp_associated_wallets)
        return total_sold


def execute_dev_selling_reporting(token_ca, liquidty_hash, telegram_user_id):
    check_dev(liquidty_hash, token_ca)


print(execute_dev_selling_reporting("B1wQUhxZAJ1EEd22dhetZ62adPwBggtvwwMBw4ooH5qN",
                                    "4nt4pJKz1Ev12RiPNyuUtLohdk4gHwgs4micBMC1VUSHVpN6hTRsW2wmVkiXdes3rS9defxnGJvBXm8mNyyEqD3U",
                                    ""))
