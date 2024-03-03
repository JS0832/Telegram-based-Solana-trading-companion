from requests import request
import asyncio
import time

solscan_header = {
    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MDY3NTM5ODAzOTQsImVtYWlsIjoic29sYmFieTMyNUBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJpYXQiOjE3MDY3NTM5ODB9.Lp77APFLV-rOnNbDzc1ob43Vp-9-KpeMe_b-fiOQrr0',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.82 Safari/537.36'
}

# stack
wallet_stack = []  # wallets to be checked
visited_wallets = []  # all wallets that have been visited
token_supply = 100000000  # will be known anyway
token_addrres = "7SU47XTwaPeeLZJkbGEWjTnPaKcTWPit6E75LhYPvby1"  # will be known
wallet_balances = []


def main(txn_hash):
    amount_sold = 0
    root = check_mint_wallet(txn_hash)
    if root == "":
        print("error not supported")
        return ""
        # check_mint_wallet(txn_hash) (until fixed set root to be something else)
    wallet_stack.append(root)  # stack begins from the root wallet
    while True:
        if len(wallet_stack) > 0:  # given the stack is not empty we know there is more to be traversed
            temp_wallet = str(
                wallet_stack.pop())  # remove the top item from the stack and it becomes the next wallet of interest
            visited_wallets.append(temp_wallet)  # Add to visited wallets
            print("checking : " + str(temp_wallet))
            # add corresponding balance
            while True:
                try:
                    balance_sheet = request('GET',
                                            "https://pro-api.solscan.io/v1.0/account/tokens?account=" + str(
                                                temp_wallet),
                                            headers=solscan_header)  # initially checks the query size requirement
                    time.sleep(0.1)
                    spl_balance = balance_sheet.json()
                    break
                except ValueError:
                    continue

            for token in spl_balance:
                if str(token["tokenAddress"]) == token_addrres:
                    wallet_balances.append(int(token["tokenAmount"]["uiAmount"]))
            time.sleep(0.1)
            tx_count_check = request('GET',
                                     "https://pro-api.solscan.io/v1.0/account/splTransfers?account=" + str(
                                         temp_wallet) + "&limit=1&offset=0",
                                     headers=solscan_header)  # initially checks the query size requirement
            spl_tx_count = tx_count_check.json()["total"]
            if spl_tx_count > 25:
                spl_tx_count = 25
            time.sleep(0.1)
            all_spl_tx = request('GET',
                                 "https://pro-api.solscan.io/v1.0/account/splTransfers?account=" + str(
                                     temp_wallet) + "&limit=" + str(spl_tx_count) + "&offset=0",
                                 headers=solscan_header)  # query all spl token transactions
            spl_transfers = all_spl_tx.json()["data"]  # all spl transfers in this current wallet
            for spl_transfer in spl_transfers:  # loop over all transaction per give wallet
                if int(spl_transfer["changeAmount"]) < 0 and str(spl_transfer["tokenAddress"]) == token_addrres:
                    temp_hash = str(spl_transfer["signature"][0])
                    time.sleep(0.1)
                    tx_info = request('GET',
                                      "https://pro-api.solscan.io/v1.0/transaction/" + str(
                                          temp_hash),
                                      headers=solscan_header)
                    tx_json = tx_info.json()
                    if "raydiumTransactions" in tx_json:
                        if len(tx_json["raydiumTransactions"]) > 0:
                            if str(tx_json["raydiumTransactions"][0]["swap"]["event"][0][
                                       "sourceOwner"]) == temp_wallet and str(
                                tx_json["raydiumTransactions"][0]["swap"]["event"][0][
                                    "destinationOwner"]) == "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":
                                amount_sold += int(
                                    float(tx_json["raydiumTransactions"][0]["swap"]["event"][0]["amount"]) / float(
                                        10) ** float(
                                        tx_json["raydiumTransactions"][0]["swap"]["event"][0]["decimals"]))
                    for tx_items in tx_json["tokenTransfers"]:
                        if str(tx_items["token"]["address"]) == token_addrres:
                            if str(tx_items["destination_owner"]) not in visited_wallets:  # seen before?
                                wallet_stack.append(str(tx_items["destination_owner"]))
        else:
            break  # done

    print(str(float(amount_sold) / float(token_supply) * float(100)) + "%")


# her we are lookign for a wallet that make a spl transfer of the total exact supply amount for a "" wallet means
# minted.
def check_mint_wallet(liquidty_add_txn_hash):
    liquidity_tx_info = request('GET',
                                "https://pro-api.solscan.io/v1.0/transaction/" + str(
                                    liquidty_add_txn_hash),
                                headers=solscan_header)

    liquidity_tx_info_json = liquidity_tx_info.json()
    signer = str(liquidity_tx_info_json["signer"][0])
    wallet_stack.append(signer)  # stack begins from the root wallet
    while True:
        if len(wallet_stack) > 0:  # given the stack is not empty we know there is more to be traversed
            temp_wallet = str(
                wallet_stack.pop())  # remove the top item from the stack and it becomes the next wallet of interest
            visited_wallets.append(temp_wallet)  # Add to visited wallets
            print("checking : " + str(temp_wallet))
            all_spl_tx = request('GET',
                                 "https://pro-api.solscan.io/v1.0/account/splTransfers?account=" + str(
                                     temp_wallet) + "&limit=" + str(10) + "&offset=0",
                                 headers=solscan_header)  # query all spl token transactions
            spl_transfers = all_spl_tx.json()["data"]  # all spl transfers in this current wallet
            for spl_transfer in spl_transfers:  # loop over all transaction per give wallet
                if str(spl_transfer["tokenAddress"]) == token_addrres:
                    temp_hash = str(spl_transfer["signature"][0])
                    time.sleep(0.1)
                    tx_info = request('GET',
                                      "https://pro-api.solscan.io/v1.0/transaction/" + str(
                                          temp_hash),
                                      headers=solscan_header)
                    tx_json = tx_info.json()
                    for tx_items in tx_json["tokenTransfers"]:
                        if str(tx_items["token"]["address"]) == token_addrres:
                            if str(tx_items["destination_owner"]) not in visited_wallets:  # seen before?
                                wallet_stack.append(str(tx_items["destination_owner"]))
        else:
            break  # done


##fix tmrw


async def poll_dev_wallet_activity():  # make it for one ping atm
    while True:
        index = 0
        for wallet in visited_wallets:
            print("checking wallet: " + str(wallet))
            time.sleep(0.1)
            try:
                balance_sheet = request('GET',
                                        "https://pro-api.solscan.io/v1.0/account/tokens?account=" + str(
                                            wallet),
                                        headers=solscan_header)  # initially checks the query size requirement
                time.sleep(0.1)
                spl_balance = balance_sheet.json()
            except ValueError as e:
                print("error checking again.")
                continue
            time.sleep(0.1)
            for token in spl_balance:
                if str(token["tokenAddress"]) == token_addrres:
                    if int(token["tokenAmount"]["uiAmount"]) < wallet_balances[index]:  # reduction (movement)
                        print("dev selling! percent of supply:" + str(
                            float(wallet_balances[index] - int(token["tokenAmount"]["uiAmount"])) / float(
                                token_supply) * float(100)))
                        wallet_balances[index] = int(token["tokenAmount"]["uiAmount"])
            index += 1
        await asyncio.sleep(3)


if __name__ == "__main__":
    main("2EFkLeUFAT8SxRBJCvnGNVzLyHvBTQL8P9ShHtvZNVU2YUJ9ZrURr3uGBJwa22hPoQZYJCVDLnBFCSaXydmy8ZQy")
    loop = asyncio.get_event_loop()
    coros = [poll_dev_wallet_activity()]
    loop.run_until_complete(asyncio.gather(*coros))
