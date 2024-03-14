from requests import request

solscan_header = {
    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
             '.eyJjcmVhdGVkQXQiOjE3MDY3NTM5ODAzOTQsImVtYWlsIjoic29sYmFieTMyNUBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJpYXQiOjE3MDY3NTM5ODB9.Lp77APFLV-rOnNbDzc1ob43Vp-9-KpeMe_b-fiOQrr0',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.82 Safari/537.36'
}


def get_name_ticker(txn_hash):
    name = ""
    symbol = ""
    tries = 2
    for x in range(tries):
        liquidity_tx_info = request('GET',
                                    "https://pro-api.solscan.io/v1.0/transaction/" + str(
                                        txn_hash),
                                    headers=solscan_header)

        liquidity_tx_info_json = liquidity_tx_info.json()
        tokens_balances = liquidity_tx_info_json["tokenBalanes"]
        for token in tokens_balances:
            if token["token"]["tokenAddress"] != "So11111111111111111111111111111111111111112":
                if 'name' in token["token"] and 'symbol' in token["token"]:
                    name = str(token["token"]["name"])
                    symbol = token["token"]["symbol"]
                    return name, symbol
                else:
                    continue
    return "NOT FOUND", "NOT FOUND"

