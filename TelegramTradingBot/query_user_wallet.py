from helius import BalancesAPI

balances_api = BalancesAPI("3e1717e1-bf69-45ae-af63-361e43b78961")
solscan_header = {
    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
             '.eyJjcmVhdGVkQXQiOjE3MDY3NTM5ODAzOTQsImVtYWlsIjoic29sYmFieTMyNUBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJpYXQiOjE3MDY3NTM5ODB9.Lp77APFLV-rOnNbDzc1ob43Vp-9-KpeMe_b-fiOQrr0',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.82 Safari/537.36'
}


def return_token_balances(wallet_address):  # up to 25 addresses return a string
    balances_string = "Solana Balance: "
    spl_balances = balances_api.get_balances(wallet_address)
    sol_balance = str(spl_balances["nativeBalance"] / 10 ** 9).replace(".", ",") + " SOL"
    balances_string += sol_balance + "\n"
    token_list = []
    tokens = spl_balances["tokens"]
    token_count = 0
    for token in tokens:
        token_ca = token["mint"]
        token_amount = str((float(token["amount"]) / float(10 ** int(token["decimals"]))))
        if token["amount"] > 0:
            balances_string += f"Spl Token: `{token_ca}` {token_amount}\n".replace(".", ",")
            token_list.append([token_ca, token_amount])
            token_count += 1
        if token_count > 20:
            break

    return balances_string


def return_specific_balance(spl_token, wallet_address):
    spl_balances = balances_api.get_balances(wallet_address)
    tokens = spl_balances["tokens"]
    for token in tokens:
        token_ca = token["mint"]
        if spl_token == str(token_ca):
            return float(token["amount"]) / float(10 ** int(token["decimals"]))  # will return 0.0 if its empty anyway
        return 0.0  # if not found
