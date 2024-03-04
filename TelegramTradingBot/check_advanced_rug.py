from solana.rpc.api import Client, Pubkey
import json
from solders.signature import Signature
import requests
from helius import BalancesAPI
import query_user_wallet

balances_api = BalancesAPI("3e1717e1-bf69-45ae-af63-361e43b78961")
URI = "https://mainnet.helius-rpc.com/?api-key=3e1717e1-bf69-45ae-af63-361e43b78961"
from requests import request

solana_client = Client(URI)

solscan_header = {
    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MDY3NTM5ODAzOTQsImVtYWlsIjoic29sYmFieTMyNUBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJpYXQiOjE3MDY3NTM5ODB9.Lp77APFLV-rOnNbDzc1ob43Vp-9-KpeMe_b-fiOQrr0',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.82 Safari/537.36'
}


def check(token_address):
    alchemy_url = "https://solana-mainnet.g.alchemy.com/v2/7I2u5DUEiE6J52ML8Yo9In0CdDk-UcnO"
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "getTokenSupply",
        "params": [str(token_address)]
    }
    alchemy_headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    get_supply_response = requests.post(alchemy_url, json=payload, headers=alchemy_headers)
    get_total_supply = int(float(get_supply_response.json()["result"]['value']["uiAmountString"]))
    holder_result = request('GET',
                            "https://pro-api.solscan.io/v1.0/token/holders?tokenAddress=" + str(
                                token_address) + "&limit=1&offset=0",
                            headers=solscan_header)
    holder_list = holder_result.json()
    if "total" in holder_list:
        if int(holder_list["total"]) < 20:
            return "Small Number of holders,Non deterministic result"
    holder_result = request('GET',
                            "https://pro-api.solscan.io/v1.0/token/holders?tokenAddress=" + str(
                                token_address) + "&limit=20&offset=0",
                            headers=solscan_header)
    holder_list = holder_result.json()
    holder_tx_per_wallet_list = []
    balance_sum = 0
    try:
        for holder in holder_list["data"]:
            spl_balance = query_user_wallet.return_specific_balance(token_address, str(holder["owner"]))
            if str(holder["owner"]) != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":  # ignore raydium
                try:
                    res = solana_client.get_signatures_for_address(
                        Pubkey.from_string(str(holder["owner"])),
                        limit=20  # Specify how much last transactions to fetch
                    )
                    transactions = json.loads(str(res.to_json()))["result"]
                    temp_count = 0
                    for tx in transactions:
                        temp_count += 1
                    holder_tx_per_wallet_list.append(temp_count)
                    if temp_count < 6:
                        balance_sum += spl_balance
                except ValueError:
                    continue
    except KeyError:
        print("error check:" + str(holder_list))
    low_tx_count_sum = sum(i <= 6 for i in holder_tx_per_wallet_list)
    supply_percent_held_by_low_tx_wallets = int(balance_sum/get_total_supply * 100)
    if low_tx_count_sum <= 3:
        return "Low"
    elif 3 < low_tx_count_sum < 6:
        return "Moderate"
    elif 6 <= low_tx_count_sum < 10:
        if supply_percent_held_by_low_tx_wallets > 30:
            return "High"
        else:
            return "Moderate"
    else:
        if supply_percent_held_by_low_tx_wallets > 30:
            return "Extremely High"
        else:
            return "High"
