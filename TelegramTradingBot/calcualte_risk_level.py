# let's order the info from most important to least


# advanced rug - sets baseline risk level number (low = 1,medium = 3,high = 6)
# the largest cumulative holder ( under 5% + 0%,5-10 +10% 10-20 +20% ,20-40 +30% 40+ +40%)
# dev sold (0 = +0% ,0-1 + 30% ,1+ +40%
# tokens sent to lp 85+ 0% ,70 or lower = +20%
# decentralisation low +5%,med+2%,highi+0%

def process_risk(advanced_rug, lcm, dev_sold, tokens_to_lp, decent):
    risk = 1
    if advanced_rug == "Moderate":  # advanced rug is the most important metric
        risk += 2
    elif advanced_rug == "High":
        risk += 5
    # now checking the largest holder
    if 5 < int(lcm) <= 10:
        risk = risk * 1.1
    elif 11 < int(lcm) < 20:
        risk = risk * 1.2
    elif 21 < int(lcm) < 30:
        risk = risk * 1.3
    elif 31 < int(lcm) < 40:
        risk = risk * 1.4
    # now check dev sell:
    if 1 > float(dev_sold) > 0:
        risk = risk * 1.3
    elif float(dev_sold) > 1:
        risk = risk * 1.4
    # now check token to lp
    if int(tokens_to_lp) < 70:
        risk = risk * 1.2
    # DECENTRALISATION
    if decent == "Moderate":
        risk = risk * 1.1
    elif decent == "Poor":
        risk = risk * 1.2
    if risk > 10:
        return "10 Extreme"
    elif risk < 4:
        return str(int(risk)) + " Low"
    elif 6 > risk > 4:
        return str(int(risk)) + " Moderate"
    elif risk > 6:
        return str(int(risk)) + " High"

