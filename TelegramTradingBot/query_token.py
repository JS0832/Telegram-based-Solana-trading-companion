# Sniper/Large holder check#
from requests import request
from helius import TransactionsAPI
from helius import BalancesAPI
import requests
import json
from solana.rpc.api import Client, Pubkey
import helius_api_key
helius_key = helius_api_key.hel_api_key
solscan_header = {
    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MDY3NTM5ODAzOTQsImVtYWlsIjoic29sYmFieTMyNUBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJpYXQiOjE3MDY3NTM5ODB9.Lp77APFLV-rOnNbDzc1ob43Vp-9-KpeMe_b-fiOQrr0',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.82 Safari/537.36'
}
transactions_api = TransactionsAPI(helius_key)
balances_api = BalancesAPI(helius_key)
# Sniper/Large holder check#
"""
    largest_holder = str(data[0])  DONE
    decentralisation = str(data[4])
    whale_holders = str(data[5])
"""


def main_query(token_ca):
    """grab token supply"""
    alchemy_url = "https://solana-mainnet.g.alchemy.com/v2/bzkveugN6acIccgGUJTetb95Sz0yo8W_"
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "getTokenSupply",
        "params": [str(token_ca)]
    }
    alchemy_headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    get_supply_response = requests.post(alchemy_url, json=payload, headers=alchemy_headers)
    token_supply = int(float(get_supply_response.json()["result"]['value']["uiAmountString"]))
    temp = check_holders(token_ca, token_supply)
    decentralisation = temp[0]
    whale_holders = temp[1]
    # largest_holder = check_for_large_holder(token_ca, token_supply)
    return ["UPDATE SOON", decentralisation, whale_holders]


def check_holders(token_address, token_supply):
    """grab decimals"""
    decimals = 0
    req = request('GET',
                  "https://pro-api.solscan.io/v1.0/token/meta?tokenAddress=" + str(token_address),
                  headers=solscan_header)
    if 'decimals' not in req.json():
        print("token has no decimals!")
    else:
        decimals = int(req.json()['decimals'])
    holder_result = request('GET',
                            "https://pro-api.solscan.io/v1.0/token/holders?tokenAddress=" + str(
                                token_address) + "&limit=13&offset=0",
                            headers=solscan_header)
    holder_list = holder_result.json()

    five_or_above = 0  # number of holders that have 5%+
    total_supply_held = 0  # amount fo supply top 10 holders hold
    amount_of_coins_for_five_percent = \
        int(float(token_supply) * float(0.05))
    # total supply * 0.05 then convert to int
    supply = token_supply
    total_held_string = ""
    five_above_string = ""
    if "total" in holder_list:
        if int(holder_list["total"]) > 12:
            iterator = 0
            for holder in holder_list["data"]:
                if iterator > 12:
                    break
                if str(holder[
                           "owner"]) != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":  # raydium pool
                    if int(float(holder["amount"]) / float(
                            10 ** int(decimals))) >= amount_of_coins_for_five_percent:
                        five_or_above += 1
                    total_supply_held += int(float(holder["amount"]) / float(10 ** decimals))
                iterator += 1
        if int(float(total_supply_held / supply) * float(100)) < 20:  # safu
            total_held_string = "Excellent : " + str(
                int(float(total_supply_held / supply) * float(100)))
        elif 40 > int(float(total_supply_held / supply) * float(100)) > 20:  # moderate risk
            total_held_string = "Moderate : " + str(
                int(float(total_supply_held / supply) * float(100)))
        else:  # high risk
            total_held_string = "Poor : " + str(
                int(float(total_supply_held / supply) * float(100)))
    return total_held_string, five_or_above


def check_for_large_holder(token_address, token_supp):  # instead of recomputing how about tracking the wallets
    # associated to largest holder
    holders = []
    URI = "https://mainnet.helius-rpc.com/?api-key="+str(helius_key)
    solana_client = Client(URI)
    holder_result = request('GET',
                            "https://pro-api.solscan.io/v1.0/token/holders?tokenAddress=" + str(
                                token_address) + "&limit=13&offset=0",
                            headers=solscan_header)
    holder_list = holder_result.json()
    if "total" in holder_list:
        if int(holder_list["total"]) > 8:
            iterator = 0
            for holder in holder_list["data"]:
                if iterator > 6:
                    break
                if str(holder["owner"]) != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":  # raydium pool
                    holders.append(str(holder["owner"]))
                iterator += 1
    all_seen_wallets = []  # helps to avoid double seen wallets
    token_addy = token_address
    token_supply = token_supp
    true_supply_held_by_top_twenty = []  # this list will show true token holdings by the top 20 holders
    for holder in holders:
        if holder not in all_seen_wallets:
            print("checking holder: " + str(holder))
            temp_associated_wallets = []  # for each holder checked (stack)
            root = holder
            temp_associated_wallets.append(root)
            all_seen_wallets.append(root)
            temp_total_spl_balance = 0
            while True:  # here traverse all wallets connected to one wallet and count the total supply holding.
                if len(temp_associated_wallets) > 0:  # means there is more to check
                    temp_wallet = str(temp_associated_wallets.pop())
                    balances = balances_api.get_balances(temp_wallet)
                    for token in balances["tokens"]:
                        if str(token["mint"]) == token_addy:
                            temp_total_spl_balance += int(float(token["amount"]) / 10 ** float(token["decimals"]))
                    res = solana_client.get_signatures_for_address(
                        Pubkey.from_string('459JAd5ibXmNdAZTUEPQ5uC9wCWBaJ1stpqunfQy96gc'),#SHOUDLTN BE THIS WALLET
                        limit=5  # Specify how much last transactions to fetch
                    )
                    transactions = json.loads(str(res.to_json()))["result"]

                    for tx_hash in transactions:  # loop over all transaction per give wallet (limit it to 20 )
                        parsed_transactions = transactions_api.get_parsed_transactions(
                            transactions=[tx_hash["signature"]])
                        if len(parsed_transactions[0]["tokenTransfers"]) > 0:
                            temp_token_transfer_counter = 0
                            for tx_items in parsed_transactions[0]["tokenTransfers"]:
                                if str(tx_items["mint"]) == token_addy:
                                    if str(tx_items["toUserAccount"]) == temp_wallet:
                                        if str(tx_items["fromUserAccount"]) not in all_seen_wallets:
                                            if str(tx_items[
                                                       "fromUserAccount"]) != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1" and str(
                                                tx_items[
                                                    "fromUserAccount"]) != "":  # because thats just a mint operation
                                                temp_associated_wallets.append(str(tx_items["fromUserAccount"]))
                                                all_seen_wallets.append(str(tx_items["fromUserAccount"]))
                                    elif str(tx_items["fromUserAccount"]) == temp_wallet:
                                        if str(tx_items["toUserAccount"]) not in all_seen_wallets:
                                            if str(tx_items[
                                                       "toUserAccount"]) != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":
                                                print("to user" + str(tx_items["toUserAccount"]))
                                                temp_associated_wallets.append(str(tx_items["toUserAccount"]))
                                                all_seen_wallets.append(str(tx_items["toUserAccount"]))
                                if temp_token_transfer_counter > 10:
                                    break
                                else:
                                    temp_token_transfer_counter += 1
                        print("checking.....")
                else:
                    percentage = int(float(temp_total_spl_balance) / float(token_supply) * float(100))
                    true_supply_held_by_top_twenty.append(percentage)  # convert it as a percentage
                    break  # done
    return max(true_supply_held_by_top_twenty)  # return max value
