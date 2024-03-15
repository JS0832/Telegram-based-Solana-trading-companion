import solana
from solana.rpc.api import Client, Pubkey
import json
from solders.signature import Signature
import requests
from helius import BalancesAPI
import query_user_wallet
import helius_api_key
from solana.exceptions import SolanaRpcException
from helius import TransactionsAPI

helius_key = helius_api_key.hel_api_key
transactions_api = TransactionsAPI(helius_key)
balances_api = BalancesAPI(helius_key)
URI = "https://mainnet.helius-rpc.com/?api-key=" + str(helius_key)
from requests import request

solana_client = Client(URI)

solscan_header = {
    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MDY3NTM5ODAzOTQsImVtYWlsIjoic29sYmFieTMyNUBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJpYXQiOjE3MDY3NTM5ODB9.Lp77APFLV-rOnNbDzc1ob43Vp-9-KpeMe_b-fiOQrr0',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.82 Safari/537.36'
}


def check(token_address):
    print("checking for advanced rug....")
    alchemy_url = "https://solana-mainnet.g.alchemy.com/v2/bzkveugN6acIccgGUJTetb95Sz0yo8W_"
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
        if int(holder_list["total"]) < 16:
            return "Too little holders"
    holder_result = request('GET',
                            "https://pro-api.solscan.io/v1.0/token/holders?tokenAddress=" + str(
                                token_address) + "&limit=16&offset=0",
                            headers=solscan_header)
    holder_list = holder_result.json()
    holder_tx_per_wallet_list = []
    incoming_transfer_count_list = []
    balance_sum = 0
    try:
        for holder in holder_list["data"]:
            if str(holder["owner"]) != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":  # ignore radium
                spl_balance = query_user_wallet.return_specific_balance(token_address, str(holder["owner"]))
                spl_transfers = request('GET',
                                        "https://pro-api.solscan.io/v1.0/account/splTransfers?account=" + str(
                                            holder["owner"]) + "&limit=16&offset=0",
                                        headers=solscan_header).json()
                incoming_transfer_count = 0
                for spl_transfer in spl_transfers["data"]:
                    if spl_transfer["tokenAddress"] == token_address and spl_transfer["changeType"] == "inc":
                        incoming_transfer_count = incoming_transfer_count + 1
                incoming_transfer_count_list.append(incoming_transfer_count)
                try:
                    tx_count = 12
                    while True:
                        try:
                            res = solana_client.get_signatures_for_address(
                                Pubkey.from_string(str(holder["owner"])),
                                limit=tx_count  # Specify how much last transactions to fetch
                            )
                            break
                        except solana.exceptions.SolanaRpcException:
                            tx_count = tx_count - 2  # decrement until we get to allowable amount
                    if tx_count == 0:  # ERROR IN THE WALLET, PROBABLY.
                        continue
                    transactions = json.loads(str(res.to_json()))["result"]
                    temp_count = 0
                    for tx in transactions:  # here I will also check for a new version of rug where the dev buys up
                        temp_count += 1
                    holder_tx_per_wallet_list.append(temp_count)
                    if temp_count < 6:
                        balance_sum += spl_balance
                except ValueError:
                    continue
    except KeyError:
        print("error check:" + str(holder_list))
    low_tx_count_sum = sum(i <= 6 for i in holder_tx_per_wallet_list)
    supply_percent_held_by_low_tx_wallets = int(balance_sum / get_total_supply * 100)
    print("advanced rug check complete.")
    if len(incoming_transfer_count_list) > 0:
        if max(incoming_transfer_count_list) > 12:
            print("Rug 2.0 likely! for token: "+str(token_address))
            return "High"
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
            print("advanced rug confirmed")
            return "Extremely High"
        else:
            return "High"

print(check("3UtWUcwFdtaMePFURciSvqyR3QqEmMJnjpmj8oX21gCs"))