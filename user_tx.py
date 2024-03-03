from requests import request
import math

header = {
    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MDY3NTM5ODAzOTQsImVtYWlsIjoic29sYmFieTMyNUBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJpYXQiOjE3MDY3NTM5ODB9.Lp77APFLV-rOnNbDzc1ob43Vp-9-KpeMe_b-fiOQrr0',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.82 Safari/537.36'
}

user_address = "AoeCdpMnpjnsYwkhjYAY4Do8Wbz3vjmKLWLXUdbiRzb1"
tx_result = request('GET',
                    "https://pro-api.solscan.io/v1.0/account/splTransfers?account=" + str(
                        user_address) + "&limit=10&offset=0",
                    headers=header)
tx_list = tx_result.json()
for user_tx in tx_list["data"]:

    if "data" in tx_list:
        print("test")

    if str(user_tx['changeType']) == "closedAccount":
        # check the tx hash
        signature = str(user_tx["signature"][0])
        burn_tx = request('GET',
                          "https://pro-api.solscan.io/v1.0/transaction/" + signature,
                          headers=header)
        json_burn_tx = burn_tx.json()
        for meta_burn_tx in json_burn_tx["parsedInstruction"]:  # confirm burn and the amount
            if meta_burn_tx["type"] == "burn":
                print(str(meta_burn_tx["params"]["mint"]))
