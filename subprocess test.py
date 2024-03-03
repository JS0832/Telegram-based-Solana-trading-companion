import subprocess


contract_address = token[0]
rpc_url = "https://mainnet.helius-rpc.com/?api-key=3e1717e1-bf69-45ae-af63-361e43b78961"
spl_executable = r'C:\\Users\MEMEdev\.local\share\solana\install\active_release\bin\spl-token.exe'
command = [spl_executable, "display", contract_address, "-u", rpc_url]
result = subprocess.run(command, capture_output=True, text=True, shell=True)

# Output the result
if result.returncode == 0:
    if "Mint authority: (not set)" not in str(result.stdout):

else:
    print("Command failed.")
    print("Error:", result.stderr)
