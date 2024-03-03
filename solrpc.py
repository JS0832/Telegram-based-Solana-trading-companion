from helius import TransactionsAPI
from helius import BalancesAPI

balances_api = BalancesAPI("3e1717e1-bf69-45ae-af63-361e43b78961")
transactions_api = TransactionsAPI("3e1717e1-bf69-45ae-af63-361e43b78961")

transactionsw = ["3yfNjUEnznU7wy5kGZntKT2ehyF6SxEYGH5EBZTdzvtQBCFEvxYraZJmBEqXBBPEPAU8WGbZaNJPSFn78GeuskC8"]
parsed_transactions = transactions_api.get_parsed_transactions(transactions=transactionsw)
print(parsed_transactions[0])



