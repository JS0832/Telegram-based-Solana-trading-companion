from helius import BalancesAPI
#for balances
balances_api = BalancesAPI("3e1717e1-bf69-45ae-af63-361e43b78961")

balances = balances_api.get_balances("5HUxqMarY94t1qQ5WV8yPgVmrjoMkXi9SzmWo2y2TU6g")
print(balances["tokens"])
#[{'tokenAccount': 'Dh6nxRE26vjAJ2ZjCzGq4HM6242bAXvCg1bSF9ubejbf', 'mint': '9hjZ8UTNrNWt3YUTHVpvzdQjNbp64NbKSDsbLqKR6BZc', 'amount': 0, 'decimals': 9}, {'tokenAccount': 'EaPnAGgRLFYfNDhCrdVL2D1pxLSBhqKwEFmeYx4393vS', 'mint': '8UcdfyJjPByAMsMJ8VH2SNJnF8cceWy426SiigPPrwZD', 'amount': 0, 'decimals': 9}, {'tokenAccount': '4brVbypVb8EYSjiNhGecAbboAU11x5H2qFHnNptBZMum', 'mint': '4hqxNjEcyaPfyjQQCtc9JDWaGQ4M1nDScCMZ9TTwY4AX', 'amount': 1907937574, 'decimals': 6}, {'tokenAccount': 'EAciNhjqAXJNfC2sk7NDTGFxCybuKN5Daw54tRAijB71', 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'amount': 2594024, 'decimals': 6}, {'tokenAccount': '362Ab79fmmJse1e1Vxchd5KcLZjFAgdEe9WeuLXhF4kZ', 'mint': 'CLJJ6QMQUDo3pEr2pPJxi5K6mLFsNrqsKEwAdiX3fLPh', 'amount': 0, 'decimals': 6}, {'tokenAccount': 'ByiHHTYD1TXUowxuxc6Rk34VXZMH528rfetEnzqJbPvj', 'mint': 'FsRKfeKHHS1CfeWhYDPGLUivNSEDGmQwUEyx1BswiFTw', 'amount': 122075680836, 'decimals': 6}]



