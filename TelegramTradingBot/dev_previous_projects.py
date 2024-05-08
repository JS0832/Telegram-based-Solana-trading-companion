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
    tx_hash_list_tokens = []  # list to store all tokens associated with the txns hash to difirenciate between other
    # projects and the crent project
    for tx_hash_tokens in liquidity_tx_info_json["tokenBalances"]:  # should be balances so they made a typo
        tx_hash_list_tokens.append(tx_hash_tokens["token"]["tokenAddress"])
    # check for signer
    dev_wallet = str(liquidity_tx_info_json["signer"][0])
    spl_transfers = request('GET',
                            "https://pro-api.solscan.io/v1.0/account/splTransfers?account=" + str(
                                dev_wallet) + "&limit=25&offset=0",
                            headers=solscan_header).json()
    token_list = []
    for spl_transfer in spl_transfers["data"]:
        if spl_transfer["changeType"] == "inc" and spl_transfer["tokenAddress"] != token_pinged and spl_transfer[
            "tokenAddress"] not in tx_hash_list_tokens:
            if spl_transfer["tokenAddress"] != "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB" and spl_transfer[
                "tokenAddress"] != "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v":  # stables
                token_list.append(spl_transfer["tokenAddress"])
    return token_list, dev_wallet
