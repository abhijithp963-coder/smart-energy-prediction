import pandas as pd
import random

data = []

devices = [
    ("Fan", 75),
    ("LED Bulb", 9),
    ("TV", 120),
    ("Fridge", 200),
    ("Laptop", 65),
    ("AC", 1500),
    ("Washing Machine", 500),
    ("Water Heater", 2000)
]

seasons = ["Summer", "Winter", "Rainy"]
houses = ["Flat", "House"]

for _ in range(5000):

    family = random.randint(1, 6)
    house = random.choice(houses)
    season = random.choice(seasons)
    sqft = random.randint(300, 2500)

    total_units = 0

    # generate random device usage
    for _ in range(random.randint(3, 7)):

        device, watt = random.choice(devices)

        qty = random.randint(1, 3)
        hours = round(random.uniform(1, 24), 2)

        # AC seasonal effect
        if device == "AC":
            if season == "Summer":
                hours += random.uniform(2, 5)
            elif season == "Winter":
                hours *= 0.3
            elif season == "Rainy":
                hours *= 0.6

        days = 30

        units = (watt * hours * days * qty) / 1000
        total_units += units

    # household scaling
    total_units *= (1 + family * 0.06)

    if house == "House":
        total_units *= 1.10
    else:
        total_units *= 0.95

    # seasonal adjustment
    if season == "Summer":
        total_units *= 1.15
    elif season == "Winter":
        total_units *= 0.90
    elif season == "Rainy":
        total_units *= 1.05

    # small randomness (real-world noise)
    total_units *= random.uniform(0.92, 1.08)

    data.append([
        family,
        house,
        sqft,
        season,
        round(total_units, 2)
    ])


df = pd.DataFrame(data, columns=[
    "FamilyMembers",
    "HouseType",
    "Sqft",
    "Season",
    "Units"
])

df.to_csv("kerala_electricity_dataset.csv", index=False)

print("✅ 5000-row Kerala realistic dataset generated successfully!")