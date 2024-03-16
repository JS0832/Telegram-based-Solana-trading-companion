# here chekc what wallet sol transfers came from
from requests import request
import json

solscan_header = {
    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MDY3NTM5ODAzOTQsImVtYWlsIjoic29sYmFieTMyNUBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJpYXQiOjE3MDY3NTM5ODB9.Lp77APFLV-rOnNbDzc1ob43Vp-9-KpeMe_b-fiOQrr0',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.82 Safari/537.36'
}


def get_funding_wallet(deployer_wallet, inital_liquidty):  # only a guesstimate
    # need to exclude exchanges
    sol_transfers = request('GET', "https://pro-api.solscan.io/v1.0/account/solTransfers?account=" + str(
        deployer_wallet) + "&limit=20&offset=0",
                            headers=solscan_header)
    sol_transfers_json = sol_transfers.json()["data"]
    for sol_transfer in sol_transfers_json:
        sol_amount = float(sol_transfer["lamport"] / 10 ** 9)
        if sol_amount >= int(inital_liquidty) - 1:  # need to exclude exchanges
            if str(sol_transfer["src"]) != deployer_wallet:
                return sol_transfer["src"]
    return ""
