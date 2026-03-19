from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

def calculate_inflation_regret(initial_amount, start_year, end_year, inflation_rate):
    years = max(0, end_year - start_year)
    future_cost = initial_amount * ((1 + inflation_rate) ** years)
    purchasing_power_loss = future_cost - initial_amount

    if initial_amount <= 0:
        regret_score = 0
    elif future_cost <= initial_amount:
        regret_score = 0
    else:
        regret_score = (purchasing_power_loss / initial_amount) * 100

    regret_score = max(0, min(100, regret_score))

    nominal_growth_pct = ((future_cost / initial_amount - 1) * 100) if initial_amount > 0 else 0
    insight = (
        f"From {start_year} to {end_year} ({years} years) at {inflation_rate*100:.2f}% inflation, "
        f"your money needs to grow to R{future_cost:,.2f} to keep buying power, "
        f"a {nominal_growth_pct:.2f}% increase."
    )

    if years > 0:
        annualized_loss = (purchasing_power_loss / years) if years else 0
        insight += f" Average purchasing power loss per year: R{annualized_loss:,.2f}."

    if regret_score < 20:
        verdict = "Probably fine"
    elif regret_score < 50:
        verdict = "Mild regret"
    elif regret_score < 80:
        verdict = "Risky decision"
    else:
        verdict = "High regret"

    return {
        "years": years,
        "future_cost": future_cost,
        "purchasing_power_loss": purchasing_power_loss,
        "regret_score": regret_score,
        "insight": insight,
        "verdict": verdict,
    }

@app.route("/", methods=["GET"])
def home():
    current_year = datetime.now().year
    return render_template("index.html", current_year=current_year)

@app.route("/result", methods=["POST"])
def result():
    description = request.form.get("description", "").strip()
    try:
        initial_amount = float(request.form.get("initial_amount", "0").replace(',', ''))
    except ValueError:
        initial_amount = 0.0

    try:
        start_year = int(request.form.get("start_year", datetime.now().year))
    except ValueError:
        start_year = datetime.now().year

    try:
        end_year = int(request.form.get("end_year", start_year))
    except ValueError:
        end_year = start_year

    try:
        inflation_rate = float(request.form.get("inflation_rate", "0")) / 100.0
    except ValueError:
        inflation_rate = 0.0

    if end_year < start_year:
        end_year = start_year

    result_data = calculate_inflation_regret(initial_amount, start_year, end_year, inflation_rate)

    return render_template(
        "result.html",
        description=description,
        initial_amount=initial_amount,
        start_year=start_year,
        end_year=end_year,
        inflation_rate=inflation_rate,
        **result_data
    )

if __name__ == "__main__":
    app.run(debug=True)
