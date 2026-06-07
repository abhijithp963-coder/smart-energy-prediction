import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import joblib

appliances = {
    "Fan": 75,
    "LED Bulb": 9,
    "TV": 120,
    "Fridge": 200,
    "Laptop": 65,
    "AC": 1500,
    "Washing Machine": 500,
    "Iron Box": 1000
}

data = []

for _ in range(2000):

    device = np.random.choice(list(appliances.keys()))
    watt = appliances[device]

    hours = np.random.randint(1, 12)
    qty = np.random.randint(1, 3)
    days = 30

    units = (watt * hours * qty * days) / 1000

    if units <= 50:
        bill = units * 3.15
    elif units <= 150:
        bill = 50*3.15 + (units-50)*4
    elif units <= 300:
        bill = 50*3.15 + 100*4 + (units-150)*5
    else:
        bill = 50*3.15 + 100*4 + 150*5 + (units-300)*6

    data.append([watt, hours, qty, units, bill])

df = pd.DataFrame(data, columns=["watt", "hours", "qty", "units", "bill"])

X = df[["watt", "hours", "qty"]]
y = df["bill"]

scaler = StandardScaler()
X = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = LinearRegression()
model.fit(X_train, y_train)

joblib.dump(model, "model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("✅ Model trained successfully")