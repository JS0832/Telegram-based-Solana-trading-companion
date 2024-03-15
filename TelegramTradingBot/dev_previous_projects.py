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
    res = solana_client.get_signatures_for_address(
        Pubkey.from_string(dev_wallet),
        limit=50  # Specify how much last transactions to fetch
    )

    spl_transfers = request('GET',
                            "https://pro-api.solscan.io/v1.0/account/splTransfers?account=" + str(
                                dev_wallet) + "&limit=50&offset=0",
                            headers=solscan_header).json()

    token_list = []

    for spl_transfer in spl_transfers["data"]:
        if spl_transfer["changeType"] == "inc" and spl_transfer["tokenAddress"] != token_pinged:
            token_list.append(spl_transfer["tokenAddress"])
    return token_list, dev_wallet


