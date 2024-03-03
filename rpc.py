from solana.rpc.api import Client
solana_client = Client("https://mainnet.helius-rpc.com/?api-key=3e1717e1-bf69-45ae-af63-361e43b78961")

solana_client.get_signatures_for_address("2AQdpHJ2JpcEgPiATUXjQxA8QmafFegfQwSLWSprPicm", limit=1)