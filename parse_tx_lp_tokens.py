from requests import request
import requests

header = {
    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MDY3NTM5ODAzOTQsImVtYWlsIjoic29sYmFieTMyNUBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJpYXQiOjE3MDY3NTM5ODB9.Lp77APFLV-rOnNbDzc1ob43Vp-9-KpeMe_b-fiOQrr0',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.82 Safari/537.36'
}
tx_hash = '2G7xUeccXbHqE2y4ifJai78ivnZ3wcGRTsLLq7Cc5m64hsVzWhoDnhe5Syjnn6ogSaLiLA8qFCy5nz9tzCaUA1EY'
result = request('GET', "https://pro-api.solscan.io/v1.0/transaction/" + tx_hash, headers=header)
transaction = result.json()
mint = ''  # the lp token address
amount = 0  # lp token amount
token_decimals = 9

alchemy_url = "https://solana-mainnet.g.alchemy.com/v2/7I2u5DUEiE6J52ML8Yo9In0CdDk-UcnO"
payload = {
    "id": 1,
    "jsonrpc": "2.0",
    "method": "getTokenSupply",
    "params": ["J4xzYCv2aBk1VxMA86k4ydAFCELGRAQZu62LnReB4HGo"]
}
alchemy_headers = {
    "accept": "application/json",
    "content-type": "application/json"
}
get_supply_response = requests.post(alchemy_url, json=payload, headers=alchemy_headers)
token_supply = int(float(get_supply_response.json()["result"]['value']["uiAmountString"]))
token_amount_sent_to_lp_pool = 0
print(token_supply)
for tx in transaction['innerInstructions'][0]['parsedInstructions']:
    if 'extra' in tx:
        # if str(tx['extra']['tokenAddress']) == "So11111111111111111111111111111111111111112" and str(tx['extra']['destinationOwner']) == "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1": #raydium authority
        # print(int(int(tx['extra']['amount'])/1000000000))
        if str(tx['extra'][
                   'tokenAddress']) == str(
            "J4xzYCv2aBk1VxMA86k4ydAFCELGRAQZu62LnReB4HGo"):  # find how many coins sent to lp pool
            print(int(int(tx['extra']['amount']) / 10 ** token_decimals))
            token_amount_sent_to_lp_pool = int(int(tx['extra']['amount']) / 10 ** token_decimals)

print(int((float(token_amount_sent_to_lp_pool) / float(token_supply)) * float(100)))
