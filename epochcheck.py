from helius import TransactionsAPI

transactions_api = TransactionsAPI("3e1717e1-bf69-45ae-af63-361e43b78961")

tx_history = transactions_api.get_parsed_transaction_history(
    address="5HUxqMarY94t1qQ5WV8yPgVmrjoMkXi9SzmWo2y2TU6g", type="TRANSFER")

print(tx_history)