from requests import request

solscan_header = {
    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MDY3NTM5ODAzOTQsImVtYWlsIjoic29sYmFieTMyNUBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJpYXQiOjE3MDY3NTM5ODB9.Lp77APFLV-rOnNbDzc1ob43Vp-9-KpeMe_b-fiOQrr0',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.82 Safari/537.36'
}
signature = "5SNVwJjXr5nkTCT88KnDit9ZqQmVDM45jBApK58smcnY8Sm598QYdLwuKDMHmuo3H9iam6iLFpufQEV1EpbQVxEA"
tx_info = request('GET',
                  "https://pro-api.solscan.io/v1.0/transaction/" + signature,
                  headers=solscan_header)
tx_info_json = tx_info.json()
token = str(tx_info_json["unknownTransfers"][0]["event"][0]["tokenAddress"])
print(token)
