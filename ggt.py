from requests import request

solscan_header = {
    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MDY3NTM5ODAzOTQsImVtYWlsIjoic29sYmFieTMyNUBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJpYXQiOjE3MDY3NTM5ODB9.Lp77APFLV-rOnNbDzc1ob43Vp-9-KpeMe_b-fiOQrr0',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.82 Safari/537.36'
}

lq_token = "9CzyviP91YCTLyf9woYQ8eSZNHJVW5VHNzjjyfZxf81"
result = request('GET',
                 "https://pro-api.solscan.io/v1.0/token/holders?tokenAddress=" + lq_token + "&limit=10&offset=0",
                 headers=solscan_header)
lp_holder = result.json()
if "data" in lp_holder:
    if str(lp_holder["total"]) == "1":
        print(str(lp_holder["data"][0][
                      "owner"]))
    elif int(lp_holder["total"]) > 1:
        print("error more than one Holder")
else:
    print("error")
