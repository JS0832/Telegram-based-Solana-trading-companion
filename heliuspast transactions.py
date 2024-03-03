from helius import TransactionsAPI

transactions_api = TransactionsAPI("3e1717e1-bf69-45ae-af63-361e43b78961")

parsed_transaction_history = transactions_api.get_parsed_transaction_history(
    address="3QJcZvfav8Rx3rREtt4FrGCT1SRnLqyqPMtJ9ioC8BQt", type="TRANSFER",="")
temp_tx_hash_list = []
for tx in parsed_transaction_history:
    if len(tx["tokenTransfers"]) > 0:
        temp_tx_hash_list.append(tx["signature"])

print(temp_tx_hash_list)
