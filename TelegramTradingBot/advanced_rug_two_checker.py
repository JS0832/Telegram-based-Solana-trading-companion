from requests import request

solscan_header = {
    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MDY3NTM5ODAzOTQsImVtYWlsIjoic29sYmFieTMyNUBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJpYXQiOjE3MDY3NTM5ODB9.Lp77APFLV-rOnNbDzc1ob43Vp-9-KpeMe_b-fiOQrr0',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.82 Safari/537.36'
}

exchange_wallets = {  # add more later
    "2ojv9BAiHUrvsm9gxDe7fJSzbNZSJcxZvf8dqmWGHG8S": "Binance 1",
    "5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9": "Binance 2",
    "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Binance 3",
    "H8sMJSCQxfKiFTCfDR3DUMLPwcRbM61LGFJ8N4dK3WjS": "Coinbase 1",
    "2AQdpHJ2JpcEgPiATUXjQxA8QmafFegfQwSLWSprPicm": "Coinbase 2",
    "GJRs4FwHtemZ5ZE9x3FNvJ8TMwitKTh21yxdRPqn7npE": "Coinbase 2",
    "FWznbcNXWQuHTawe9RxvQ2LdCENssh12dsznf4RiouN5": "Kraken",
    "ASTyfSima4LLAdDgoFGkgqoKowG1LZFDr9fAQrg7iaJZ": "MEXC",
    "AC5RDfQFmDS1deWZos921JfqscXdByf8BKHs5ACWjtW2": "Bybit",
    "BmFdpraQhkiDQE6SnfG5omcA1VwzqfXrwtNYBwWTymy6": "Kucoin"
}

black_list = ["FLiPggWYQyKVTULFWMQjAk26JfK5XRCajfyTmD5weaZ7",
              "Habp5bncMSsBC3vkChyebepym5dcTNRYeg2LVG464E96"]  # soem bots?


def check_for_common_funding_wallets(token_ca):  # advanced rug 2.0 #need to exclude exchanges
    holder_tx_list = []
    holder_result = request('GET',
                            "https://pro-api.solscan.io/v1.0/token/holders?tokenAddress=" + str(
                                token_ca) + "&limit=20&offset=0",
                            headers=solscan_header)
    holder_list = holder_result.json()
    for holder in holder_list["data"]:
        sub_list_builder = []
        if str(holder["owner"]) != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":  # (ignore raydium)
            sol_transfers = request('GET', "https://pro-api.solscan.io/v1.0/account/solTransfers?account=" + str(
                holder["owner"]) + "&limit=10&offset=0",
                                    headers=solscan_header)
            sol_transfers_json = sol_transfers.json()["data"]
            tx_count = 0
            for sol_transfer in sol_transfers_json:
                if str(sol_transfer["src"]) not in exchange_wallets and str(sol_transfer["src"]) not in black_list:
                    sub_list_builder.append(sol_transfer["src"])
                if tx_count > 10:
                    break
                tx_count += 1
            holder_tx_list.append(sub_list_builder)
    common_wallet_count = 0
    wallet_index_one = 0
    # print(holder_tx_list)
    for holder_associated_wallets in holder_tx_list:
        for index in range(wallet_index_one + 1, len(holder_tx_list)):
            # print(wallet_index_one, index)
            if len(list(set(holder_associated_wallets).intersection(holder_tx_list[index]))) > 0:
                print(list(set(holder_associated_wallets).intersection(holder_tx_list[index])))
                common_wallet_count += 1
        wallet_index_one += 1
    if common_wallet_count / 20 * 100 > 30:
        return True
    else:
        return False
