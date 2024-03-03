from requests import request
from helius import TransactionsAPI
from helius import BalancesAPI

solscan_header = {
    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MDY3NTM5ODAzOTQsImVtYWlsIjoic29sYmFieTMyNUBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJpYXQiOjE3MDY3NTM5ODB9.Lp77APFLV-rOnNbDzc1ob43Vp-9-KpeMe_b-fiOQrr0',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.82 Safari/537.36'
}
transactions_api = TransactionsAPI("3e1717e1-bf69-45ae-af63-361e43b78961")
balances_api = BalancesAPI("3e1717e1-bf69-45ae-af63-361e43b78961")
transactions_api = TransactionsAPI("3e1717e1-bf69-45ae-af63-361e43b78961")


def main():
    token = "3WthbuHxUxD9DpYezeSxa5KH3LfpJpseGHtS1DiSRpfr"
    check_for_large_holder(token, 1000000000)


# optimise and possibly show updates
def check_for_large_holder(token_address, token_supp):
    holders = []
    holder_result = request('GET',
                            "https://pro-api.solscan.io/v1.0/token/holders?tokenAddress=" + str(
                                token_address) + "&limit=13&offset=0",
                            headers=solscan_header)
    holder_list = holder_result.json()
    if "total" in holder_list:
        if int(holder_list["total"]) > 8:
            iterator = 0
            for holder in holder_list["data"]:
                if iterator > 8:
                    break
                if str(holder["owner"]) != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":  # raydium pool
                    holders.append(str(holder["owner"]))
                iterator += 1
    all_seen_wallets = []  # helps to avoid double seen wallets
    token_addy = token_address
    token_supply = token_supp
    true_supply_held_by_top_twenty = []  # this list will show true token holdings by the top 20 holders
    for holder in holders:
        if holder not in all_seen_wallets:
            print("checking holder: " + str(holder))
            temp_associated_wallets = []  # for each holder checked (stack)
            root = holder
            temp_associated_wallets.append(root)
            all_seen_wallets.append(root)
            temp_total_spl_balance = 0
            while True:  # here traverse all wallets connected to one wallet and count the total supply holding.
                if len(temp_associated_wallets) > 0:  # means there is more to check
                    temp_wallet = str(temp_associated_wallets.pop())
                    balances = balances_api.get_balances(temp_wallet)
                    for token in balances["tokens"]:
                        if str(token["mint"]) == token_addy:
                            temp_total_spl_balance += int(float(token["amount"]) / 10 ** float(token["decimals"]))
                    try:
                        parsed_transaction_history = transactions_api.get_parsed_transaction_history(
                            address=temp_wallet, type="TRANSFER")
                    except ValueError:
                        'this means there arent any transfers so we can move on'
                        continue
                    temp_tx_hash_list = []
                    for tx in parsed_transaction_history:
                        if len(tx["tokenTransfers"]) > 0:
                            temp_tx_hash_list.append(tx["signature"])
                    for tx_hash in temp_tx_hash_list:  # loop over all transaction per give wallet
                        parsed_transactions = transactions_api.get_parsed_transactions(transactions=[tx_hash])
                        if len(parsed_transactions[0]["tokenTransfers"]) > 0:
                            for tx_items in parsed_transactions[0]["tokenTransfers"]:
                                if str(tx_items["mint"]) == token_addy:
                                    if str(tx_items["toUserAccount"]) == temp_wallet:
                                        if str(tx_items["fromUserAccount"]) not in all_seen_wallets:
                                            if str(tx_items[
                                                       "fromUserAccount"]) != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1" and str(
                                                tx_items[
                                                    "fromUserAccount"]) != "":  # because thats just a mint operation
                                                temp_associated_wallets.append(str(tx_items["fromUserAccount"]))
                                                all_seen_wallets.append(str(tx_items["fromUserAccount"]))
                                    elif str(tx_items["fromUserAccount"]) == temp_wallet:
                                        if str(tx_items["toUserAccount"]) not in all_seen_wallets:
                                            if str(tx_items[
                                                       "toUserAccount"]) != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":
                                                print("to user" + str(tx_items["toUserAccount"]))
                                                temp_associated_wallets.append(str(tx_items["toUserAccount"]))
                                                all_seen_wallets.append(str(tx_items["toUserAccount"]))
                else:
                    percentage = float(temp_total_spl_balance) / float(token_supply) * float(100)
                    true_supply_held_by_top_twenty.append(str(percentage) + " %")  # convert it as a percentage
                    break  # done
    print(all_seen_wallets)
    print(true_supply_held_by_top_twenty)


if __name__ == "__main__":
    main()
