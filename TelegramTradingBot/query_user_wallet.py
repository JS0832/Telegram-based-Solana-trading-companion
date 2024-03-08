from helius import BalancesAPI

balances_api = BalancesAPI("f28fd952-90ec-44cd-a8f2-e54b2481d7a8")


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
    print(wallet_address)
    spl_balances = balances_api.get_balances(wallet_address)
    tokens = spl_balances["tokens"]
    for token in tokens:
        token_ca = token["mint"]
        if spl_token == str(token_ca):
            return float(token["amount"]) / float(10 ** int(token["decimals"]))  # will return 0.0 if its empty anyway
        return 0.0  # if not found
