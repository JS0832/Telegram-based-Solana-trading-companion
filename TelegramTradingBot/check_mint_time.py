# check for the mint time
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


def check_mint_epoch(txn_hash, token_pinged, token_supply):
    liquidity_tx_info = request('GET',
                                "https://pro-api.solscan.io/v1.0/transaction/" + str(
                                    txn_hash),
                                headers=solscan_header)
    liquidity_tx_info_json = liquidity_tx_info.json()
    dev_wallet = str(liquidity_tx_info_json["signer"][0])
    spl_transfers = request('GET',
                            "https://pro-api.solscan.io/v1.0/account/splTransfers?account=" + str(
                                dev_wallet) + "&limit=50&offset=0",
                            headers=solscan_header).json()
    for spl_transfer in spl_transfers["data"]:
        if spl_transfer["changeType"] == "inc" and spl_transfer["tokenAddress"] == token_pinged:
            if int(float(spl_transfer["changeAmount"])/10**float(spl_transfer["decimals"])) == token_supply:
                return int(spl_transfer["blockTime"])
    return 0


check_mint_epoch("43D7uBvaoDMPy2iQnuKxNAkdWRugyGXGQJRT3u5SdRXDrQqCGWArb5ayVYF9Gk6VnWEqWAGG8Kcm3rwFziezoXrH",
                 "539xJaEwNkSm42ia6U2LnSDAAWH1QJSsynn1vMb7KRkF", "")
