from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
from datetime import datetime
import matplotlib.pyplot as plt

app = Flask(__name__)

last_result = {}

# --------------------------------
# CALCULATE UNITS
# --------------------------------
def calculate_units(devices, season, house):

    total = 0

    for d in devices:

        watt = float(d["watt"])
        hours = float(d["hours"])
        qty = float(d["qty"])

        days = 30

        units = (watt * hours * qty * days) / 1000

        total += units

    # SEASON EFFECT

    if season == "Summer":
        total *= 1.15

    elif season == "Winter":
        total *= 0.90

    elif season == "Rainy":
        total *= 1.05

    # HOUSE EFFECT

    if house == "House":
        total *= 1.10

    elif house == "Flat":
        total *= 0.95

    elif house == "Office":
        total *= 1.25

    return round(total, 2)


# --------------------------------
# BILL CALCULATION
# --------------------------------
def calculate_bill(units):

    if units <= 50:
        return units * 3.15

    elif units <= 150:
        return 50 * 3.15 + (units - 50) * 4

    elif units <= 300:
        return 50 * 3.15 + 100 * 4 + (units - 150) * 5

    else:
        return 50 * 3.15 + 100 * 4 + 150 * 5 + (units - 300) * 6


# --------------------------------
# HOME PAGE
# --------------------------------
@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------
# PREDICTION
# --------------------------------
@app.route("/predict", methods=["POST"])
def predict():

    season = request.form["season"]
    house = request.form["house"]

    device_names = request.form.getlist("device[]")
    watts = request.form.getlist("watt[]")
    hours = request.form.getlist("hours[]")
    minutes = request.form.getlist("minutes[]")
    qtys = request.form.getlist("qty[]")

    devices = []

    labels = []
    values = []

    for name, w, h, m, q in zip(
        device_names,
        watts,
        hours,
        minutes,
        qtys
    ):

        if w and h and q:

            m = float(m) if m else 0

            total_hours = float(h) + (m / 60)

            unit = (
                float(w)
                * total_hours
                * float(q)
                * 30
            ) / 1000

            labels.append(name)
            values.append(unit)

            devices.append({
                "device": name,
                "watt": w,
                "hours": total_hours,
                "qty": q
            })

    # --------------------------------
    # BAR GRAPH
    # --------------------------------
    plt.figure(figsize=(5,4))

    plt.bar(labels, values)

    plt.xticks(rotation=20)

    plt.title("Appliance Comparison")

    plt.tight_layout()

    plt.savefig("static/bar.png")

    plt.close()

    # --------------------------------
    # LINE GRAPH
    # --------------------------------
    plt.figure(figsize=(5,4))

    plt.plot(labels, values, marker="o")

    plt.xticks(rotation=20)

    plt.title("Usage Trend")

    plt.tight_layout()

    plt.savefig("static/line.png")

    plt.close()

    # --------------------------------
    # PIE CHART
    # --------------------------------
    plt.figure(figsize=(5,4))

    plt.pie(values, labels=labels, autopct="%1.1f%%")

    plt.title("Energy Distribution")

    plt.tight_layout()

    plt.savefig("static/pie.png")

    plt.close()

    # --------------------------------
    # CALCULATE RESULT
    # --------------------------------
    units = calculate_units(devices, season, house)

    bill = round(calculate_bill(units), 2)

    global last_result

    last_result = {
        "units": units,
        "bill": bill,
        "season": season,
        "house": house,
        "devices": devices
    }

    return render_template(
        "index.html",
        units=units,
        bill=bill,
        daily=round(units / 30, 2),
        yearly=round(bill * 12, 2)
    )


# --------------------------------
# PDF DOWNLOAD
# --------------------------------
@app.route("/download")
def download():

    file = "bill.pdf"

    c = canvas.Canvas(file)

    y = 800

    # TITLE
    c.setFont("Helvetica-Bold", 18)

    c.drawString(150, y, "SMART ENERGY REPORT")

    y -= 40

    c.setFont("Helvetica", 12)

    c.drawString(50, y, f"Date: {datetime.now()}")

    y -= 25

    c.drawString(50, y, f"House Type: {last_result.get('house')}")

    y -= 25

    c.drawString(50, y, f"Season: {last_result.get('season')}")

    y -= 25

    c.drawString(50, y, f"Total Units: {last_result.get('units')}")

    y -= 25

    c.drawString(50, y, f"Estimated Bill: ₹{last_result.get('bill')}")

    y -= 40

    # APPLIANCE DETAILS
    c.setFont("Helvetica-Bold", 13)

    c.drawString(50, y, "APPLIANCE DETAILS")

    y -= 30

    c.setFont("Helvetica", 11)

    for d in last_result.get("devices", []):

        text = (
            f"{d['device']} | "
            f"{d['watt']}W | "
            f"{round(float(d['hours']),2)} hrs | "
            f"Qty: {d['qty']}"
        )

        c.drawString(50, y, text)

        y -= 20

        if y < 120:

            c.showPage()

            y = 800

    # --------------------------------
    # GRAPH PAGE
    # --------------------------------
    c.showPage()

    c.setFont("Helvetica-Bold", 18)

    c.drawString(170, 800, "ENERGY ANALYSIS GRAPHS")

    # BAR GRAPH
    c.setFont("Helvetica-Bold", 12)

    c.drawString(50, 760, "1. Appliance Comparison")

    c.drawImage(
        "static/bar.png",
        50,
        520,
        width=220,
        height=180
    )

    # LINE GRAPH
    c.drawString(320, 760, "2. Usage Trend")

    c.drawImage(
        "static/line.png",
        320,
        520,
        width=220,
        height=180
    )

    # PIE GRAPH
    c.drawString(180, 470, "3. Energy Distribution")

    c.drawImage(
        "static/pie.png",
        150,
        180,
        width=250,
        height=250
    )

    # CREATOR
    c.setFont("Helvetica-Bold", 13)

    c.drawString(170, 120, "Created and Designed By")

    c.setFillColorRGB(0, 0, 1)

    c.drawString(245, 95, "ABHIJITH P")

    c.save()

    return send_file(file, as_attachment=True)


# --------------------------------
# RUN APP
# --------------------------------
if __name__ == "__main__":
    app.run(debug=True)