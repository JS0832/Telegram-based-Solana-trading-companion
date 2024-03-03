from requests import request

header = {
    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MDY3NTM5ODAzOTQsImVtYWlsIjoic29sYmFieTMyNUBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJpYXQiOjE3MDY3NTM5ODB9.Lp77APFLV-rOnNbDzc1ob43Vp-9-KpeMe_b-fiOQrr0',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.82 Safari/537.36'
}

token_address = "AoeaVeghbrYfr2qoDbxizxbkRQXteZbj5oCpNuSmtnDZ"
holder_result = request('GET',
                        "https://pro-api.solscan.io/v1.0/token/holders?tokenAddress=" + str(
                            token_address) + "&limit=13&offset=0",
                        headers=header)

holder_list = holder_result.json()
five_or_above = 0  # number of holders that have 5%+
total_supply_held = 0  # amount fo supply top 10 holders hold
amount_of_coins_for_five_percent = 50000000  # total supply * 0.05 then convert to int
supply = 1000000000
token = [2]
total_held_string = ""
five_above_string = ""
if "total" in holder_list:
    if int(holder_list["total"]) > 12:
        iterator = 0
        for holder in holder_list["data"]:
            if iterator > 12:
                break
            if str(holder["owner"]) != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":  # raydium pool
                if int(float(holder["amount"]) / float(10 ** token[0])) >= amount_of_coins_for_five_percent:
                    five_or_above += 1
                total_supply_held += int(float(holder["amount"]) / float(10 ** token[0]))
            iterator += 1
    if int(float(total_supply_held / supply) * float(100)) < 20:  # safu
        total_held_string = "well decentralised : "+str(int(float(total_supply_held / supply) * float(100)))
    elif 40 > int(float(total_supply_held / supply) * float(100)) > 20:  # moderate risk
        total_held_string = "moderately decentralised : " + str(int(float(total_supply_held / supply) * float(100)))
    else:  # high risk
        total_held_string = "(danger) poorly decentralised : " + str(int(float(total_supply_held / supply) * float(100)))
    five_above_string = "number of holders holding more than 5%(in top ten) : "+str(five_or_above)
print(total_held_string)
print(five_above_string)
