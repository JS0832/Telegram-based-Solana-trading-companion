from solana.rpc.api import Client
from solana.Publickey import PublicKey
from solana.rpc.types import TokenAccountOpts

solana_client = Client("https://mainnet.helius-rpc.com/?api-key=3e1717e1-bf69-45ae-af63-361e43b78961")
pub_key = PublicKey("GgPpTKg78vmzgDtP1DNn72CHAYjRdKY7AV6zgszoHCSa")
mint_account = "1YDQ35V8g68FGvcT85haHwAXv1U7XMzuc4mZeEXfrjE"
print(solana_client.get_token_accounts_by_owner(pub_key, TokenAccountOpts(mint=mint_account)))
