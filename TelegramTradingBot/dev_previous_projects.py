from solana.rpc.api import Client, Pubkey
import json
from helius import TransactionsAPI
from requests import request
import helius_api_key

helius_key = helius_api_key.hel_api_key
transactions_api = TransactionsAPI(helius_key)
URI = "https://mainnet.helius-rpc.com/?api-key=" + str(helius_key)
solana_client = Client(URI)

solscan_header = {
    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
             '.eyJjcmVhdGVkQXQiOjE3MDY3NTM5ODAzOTQsImVtYWlsIjoic29sYmFieTMyNUBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJpYXQiOjE3MDY3NTM5ODB9.Lp77APFLV-rOnNbDzc1ob43Vp-9-KpeMe_b-fiOQrr0',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.82 Safari/537.36'
}


def check_previous_project(txn_hash,
                           token_pinged):  # here check if the token has rayidum liquidty pool as hodler in it yet (soon add this)
    # here check for dev wallet
    liquidity_tx_info = request('GET',
                                "https://pro-api.solscan.io/v1.0/transaction/" + str(
                                    txn_hash),
                                headers=solscan_header)

    liquidity_tx_info_json = liquidity_tx_info.json()
    # check for signer
    dev_wallet = str(liquidity_tx_info_json["signer"][0])
    return [], dev_wallet  # for now
    res = solana_client.get_signatures_for_address(
        Pubkey.from_string(dev_wallet),
        limit=25  # Specify how much last transactions to fetch
    )
    transactions = json.loads(str(res.to_json()))["result"]
    token_list = []
    tokens_count = 0
    for spl_transfer in transactions:  # loop over all transaction per give wallet
        parsed_transactions = transactions_api.get_parsed_transactions(transactions=[spl_transfer["signature"]])
        if parsed_transactions[0]["type"] == "TOKEN_MINT":
            temp_token_list = []
            for token_transfer in parsed_transactions[0]["tokenTransfers"]:
                if token_transfer["fromUserAccount"] == "":
                    if token_transfer["mint"] != token_pinged:
                        temp_token_list.append(token_transfer["mint"])
                        tokens_count += 1
                        if tokens_count > 3:
                            return token_list + temp_token_list
            token_list = token_list + temp_token_list
    return token_list, dev_wallet
