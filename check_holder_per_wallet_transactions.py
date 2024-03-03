# if a token have many wallets that each have small amount of trasnactions then is a SCAM


from solana.rpc.api import Client, Pubkey
import json

URI = "https://mainnet.helius-rpc.com/?api-key=3e1717e1-bf69-45ae-af63-361e43b78961"  # "https://api.devnet.solana.com" | "https://api.mainnet-beta.solana.com"

solana_client = Client(URI)

res = solana_client.get_signatures_for_address(
    Pubkey.from_string('459JAd5ibXmNdAZTUEPQ5uC9wCWBaJ1stpqunfQy96gc'),
    limit=20  # Specify how much last transactions to fetch
)
transactions = json.loads(str(res.to_json()))["result"]

temp_holders = solana_client.get_token_largest_accounts(Pubkey.from_string("83skbsTN4n2XcLyJssKJArP6tESUY8NDhv7hGKHW5Fux"))

print(json.loads(str(temp_holders.to_json()))["result"]["value"])
