# here calculate if the dev sold anything so far and add their wallets for polling later
from requests import request
import time
from solana.exceptions import SolanaRpcException
from requests import request
from helius import TransactionsAPI
from helius import BalancesAPI
import json
from solana.rpc.api import Client, Pubkey
import requests
import solana
solscan_header = {
    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MDY3NTM5ODAzOTQsImVtYWlsIjoic29sYmFieTMyNUBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJpYXQiOjE3MDY3NTM5ODB9.Lp77APFLV-rOnNbDzc1ob43Vp-9-KpeMe_b-fiOQrr0',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.82 Safari/537.36'
}
transactions_api = TransactionsAPI("f28fd952-90ec-44cd-a8f2-e54b2481d7a8")
balances_api = BalancesAPI("f28fd952-90ec-44cd-a8f2-e54b2481d7a8")
alchemy_url = "https://solana-mainnet.g.alchemy.com/v2/bzkveugN6acIccgGUJTetb95Sz0yo8W_"


def check_dev(txn_hash, token_d):  # instead of recomputing how about tracking the wallets
    print("checking dev selling activity... for token: "+str(token_d))
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "getTokenSupply",
        "params": [str(token_d)]
    }
    alchemy_headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    get_supply_response = requests.post(alchemy_url, json=payload, headers=alchemy_headers)
    token_supply = int(float(get_supply_response.json()["result"]['value']["uiAmountString"]))
    liquidity_tx_info = request('GET',
                                "https://pro-api.solscan.io/v1.0/transaction/" + str(
                                    txn_hash),
                                headers=solscan_header)

    liquidity_tx_info_json = liquidity_tx_info.json()
    root = str(liquidity_tx_info_json["signer"][0])
    token_address = token_d
    URI = "https://mainnet.helius-rpc.com/?api-key=f28fd952-90ec-44cd-a8f2-e54b2481d7a8"
    solana_client = Client(URI)
    all_seen_wallets = []
    temp_associated_wallets = []  # (stack) for all associated wallets
    if root == "":
        return "error"
    temp_associated_wallets.append(root)
    all_seen_wallets.append(root)
    total_sold = 0
    while True:  # here traverse all wallets connected to one wallet and count the total supply holding.
        if len(temp_associated_wallets) > 0:
            pass
        else:
            break  # done
        temp_wallet = temp_associated_wallets.pop()
        print("checking " + str(temp_wallet))
        tx_count = 12
        while True:
            try:
                res = solana_client.get_signatures_for_address(
                    Pubkey.from_string(temp_wallet),
                    limit=tx_count  # Specify how much last transactions to fetch
                )
                break
            except solana.exceptions.SolanaRpcException:
                tx_count = tx_count - 2  # decrement until we get to allowable amount
        transactions = json.loads(str(res.to_json()))["result"]
        for tx_hash in transactions:
            if str(tx_hash["signature"]) != txn_hash:  # ignoring liquidty add
                parsed_transactions = transactions_api.get_parsed_transactions(transactions=[tx_hash["signature"]])
                if len(parsed_transactions[0]["tokenTransfers"]) > 0:
                    for tx_items in parsed_transactions[0]["tokenTransfers"]:
                        if str(tx_items["mint"]) == token_address:
                            if str(tx_items["fromUserAccount"]) == temp_wallet:  # current user sending to another user
                                if str(tx_items["toUserAccount"]) not in all_seen_wallets and str(
                                        tx_items["toUserAccount"]) != "":
                                    if str(tx_items["toUserAccount"]) != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":
                                        temp_associated_wallets.append(str(tx_items["toUserAccount"]))
                                        print("sent " + str(tx_items["toUserAccount"]))
                                    else:
                                        total_sold = total_sold + int(tx_items["tokenAmount"])
                            elif str(tx_items["toUserAccount"]) == temp_wallet:  # sends tokens from current wallet
                                if str(tx_items[
                                           "fromUserAccount"]) != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1" and str(
                                    tx_items["fromUserAccount"]) not in all_seen_wallets and str(
                                    tx_items["fromUserAccount"]) != "":
                                    print("received from wallet " + str(tx_items["toUserAccount"]))
                                    temp_associated_wallets.append(str(tx_items["fromUserAccount"]))
        all_seen_wallets.append(temp_wallet)
    print("for token "+str(token_d)+" dev sold: "+str(total_sold / token_supply * 100))
    return total_sold / token_supply * 100, all_seen_wallets  # dev selling amount in relation to the total supply


def check_wallet_balanced(list_of_wallets, spl_token):
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "getTokenSupply",
        "params": [str(spl_token)]
    }
    alchemy_headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    get_supply_response = requests.post(alchemy_url, json=payload, headers=alchemy_headers)
    token_supply = int(float(get_supply_response.json()["result"]['value']["uiAmountString"]))
    temp_total_spl_balance = 0
    for wallet in list_of_wallets:
        balances = balances_api.get_balances(wallet)
        for token in balances["tokens"]:
            if str(token["mint"]) == spl_token:
                temp_total_spl_balance = temp_total_spl_balance + int(
                    float(token["amount"]) / 10 ** float(token["decimals"]))
    return int(temp_total_spl_balance / token_supply * 100)
