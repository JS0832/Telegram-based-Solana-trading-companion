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
token_addrres = "2Zj2FHP84q9WhEzVyNinnGuES8qKC9ht7TGn8wbz7rc5"  # will be known
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


# her we are looking for a wallet that make a spl transfer of the total exact supply amount for a "" wallet means
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
            spl_transfers = all_spl_tx.json()  # all spl transfers in this current wallet
            for spl_transfer in spl_transfers["data"]:  # loop over all transaction per give wallet
                if str(spl_transfer["tokenAddress"]) == token_addrres:
                    if str(spl_transfer["changeType"]) == "inc":
                        if int(float(int(spl_transfer["changeAmount"])) / float(
                                10 ** int(spl_transfer["decimals"]))) == token_supply:
                            return str(signer)
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
            return str(signer)
        return ""

def check_dev(txn_hash):  # instead of recomputing how about tracking the wallets
    URI = "https://mainnet.helius-rpc.com/?api-key=3e1717e1-bf69-45ae-af63-361e43b78961"
    solana_client = Client(URI)
    all_seen_wallets = []
    true_supply_held_by_top_twenty = []  # this list will show true token holdings by the top 20 holders

    temp_associated_wallets = []  # for each holder checked (stack)
    root =
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
            res = solana_client.get_signatures_for_address(
                Pubkey.from_string('459JAd5ibXmNdAZTUEPQ5uC9wCWBaJ1stpqunfQy96gc'),
                limit=5  # Specify how much last transactions to fetch
            )
            transactions = json.loads(str(res.to_json()))["result"]

            for tx_hash in transactions:  # loop over all transaction per give wallet (limit it to 20 )
                parsed_transactions = transactions_api.get_parsed_transactions(
                    transactions=[tx_hash["signature"]])
                if len(parsed_transactions[0]["tokenTransfers"]) > 0:
                    temp_token_transfer_counter = 0
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
                        if temp_token_transfer_counter > 10:
                            break
                        else:
                            temp_token_transfer_counter += 1
                print("checking.....")
        else:
            percentage = int(float(temp_total_spl_balance) / float(token_supply) * float(100))
            true_supply_held_by_top_twenty.append(percentage)  # convert it as a percentage
                break  # done
    return max(true_supply_held_by_top_twenty)  # return max value

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

def execute_dev_selling_reporting(token_ca,liquidty_hash,telegram_user_id):

if __name__ == "__main__":
    main("2EFkLeUFAT8SxRBJCvnGNVzLyHvBTQL8P9ShHtvZNVU2YUJ9ZrURr3uGBJwa22hPoQZYJCVDLnBFCSaXydmy8ZQy")
    loop = asyncio.get_event_loop()
    coros = [poll_dev_wallet_activity()]
    loop.run_until_complete(asyncio.gather(*coros))
