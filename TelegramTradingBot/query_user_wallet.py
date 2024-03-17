from helius import BalancesAPI
import helius_api_key
import get_token_name_ticker

helius_key = helius_api_key.hel_api_key
balances_api = BalancesAPI(helius_key)
# binance,mexc,kraken,coinbase ect....


exchange_wallets = {  # add more later
    "2ojv9BAiHUrvsm9gxDe7fJSzbNZSJcxZvf8dqmWGHG8S": "Binance 1",
    "5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9": "Binance 2",
    "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Binance 3",
    "H8sMJSCQxfKiFTCfDR3DUMLPwcRbM61LGFJ8N4dK3WjS": "Coinbase 1",
    "2AQdpHJ2JpcEgPiATUXjQxA8QmafFegfQwSLWSprPicm": "Coinbase 2",
    "GJRs4FwHtemZ5ZE9x3FNvJ8TMwitKTh21yxdRPqn7npE": "Coinbase 2",
    "FWznbcNXWQuHTawe9RxvQ2LdCENssh12dsznf4RiouN5": "Kraken",
    "ASTyfSima4LLAdDgoFGkgqoKowG1LZFDr9fAQrg7iaJZ": "MEXC",
    "AC5RDfQFmDS1deWZos921JfqscXdByf8BKHs5ACWjtW2": "Bybit"
}


def return_token_balances(wallet_address):  # up to 25 addresses return a string
    balances_string = "🟣 Solana Balance : "
    spl_balances = balances_api.get_balances(wallet_address)
    sol_balance = str(int(spl_balances["nativeBalance"] / 10 ** 9)).replace(".", ",") + " SOL"
    if wallet_address in exchange_wallets:
        balances_string += sol_balance + " 🟨" + str(exchange_wallets[wallet_address]) + "🟨 \n"
    else:
        balances_string += sol_balance + "\n"
    token_list = []
    tokens = spl_balances["tokens"]
    token_count = 0
    # balances_string += "\n"
    '''
    token_count = 0
    for token in tokens:
        token_ca = token["mint"]
        if token_ca == "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB":
            token_ca = "USDT"
        elif token_ca == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v":
            token_ca = "USDC"
        token_amount = str((float(token["amount"]) / float(10 ** int(token["decimals"]))))
        if token["amount"] > 0:
            if token_ca != "USCD" and token_ca != "USDT":
                balances_string += f"🖤 [Token](https://dexscreener.com/solana/{token_ca})\n"
            else:
                balances_string += f"🖤 {token_ca}\n"
            token_list.append([token_ca, token_amount])
            token_count += 1
        if token_count > 3:
            break
        token_count += 1

    if token_count == 0:
        balances_string += " None Found"
    '''
    return balances_string


def return_specific_balance(spl_token, wallet_address):
    spl_balances = balances_api.get_balances(wallet_address)
    tokens = spl_balances["tokens"]
    for token in tokens:
        token_ca = token["mint"]
        if spl_token == str(token_ca):
            return float(token["amount"]) / float(10 ** int(token["decimals"]))  # will return 0.0 if its empty anyway
        return 0.0  # if not found
