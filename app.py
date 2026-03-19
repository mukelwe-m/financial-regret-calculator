from flask import Flask, jsonify, redirect, render_template, request, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inflation_regret.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Calculation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    initial_amount = db.Column(db.Float, nullable=False)
    start_year = db.Column(db.Integer, nullable=False)
    end_year = db.Column(db.Integer, nullable=False)
    inflation_rate = db.Column(db.Float, nullable=False)
    inflation_source = db.Column(db.String(50), nullable=False)
    future_cost = db.Column(db.Float, nullable=False)
    purchasing_power_loss = db.Column(db.Float, nullable=False)
    regret_score = db.Column(db.Float, nullable=False)
    verdict = db.Column(db.String(30), nullable=False)
    insight = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


def fetch_average_inflation_rate(start_year, end_year, country_code="ZA"):
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/FP.CPI.TOTL.ZG"
    params = {
        "format": "json",
        "per_page": 2000,
        "date": f"{start_year}:{end_year}",
    }

    try:
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        payload = response.json()

        if not isinstance(payload, list) or len(payload) < 2:
            return None

        rows = payload[1] or []
        values = [row.get("value") for row in rows if row.get("value") is not None]

        if not values:
            return None

        return sum(values) / len(values)
    except (requests.RequestException, ValueError, TypeError):
        return None


def build_projection(initial_amount, start_year, end_year, inflation_rate):
    if end_year < start_year:
        end_year = start_year

    points = []
    for year in range(start_year, end_year + 1):
        years_elapsed = year - start_year
        projected_cost = initial_amount * ((1 + inflation_rate) ** years_elapsed)
        points.append({"year": year, "value": round(projected_cost, 2)})

    return points

def calculate_inflation_regret(initial_amount, start_year, end_year, inflation_rate):
    years = max(0, end_year - start_year)
    future_cost = initial_amount * ((1 + inflation_rate) ** years)
    purchasing_power_loss = future_cost - initial_amount

    loss_percent = (purchasing_power_loss / initial_amount) * 100 if initial_amount > 0 else 0
    duration_factor = min(100, years * 3)
    inflation_factor = min(100, (inflation_rate * 100) * 8)

    if initial_amount <= 0 or future_cost <= initial_amount:
        regret_score = 0
    else:
        regret_score = (0.6 * loss_percent) + (0.25 * duration_factor) + (0.15 * inflation_factor)

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

    if regret_score >= 50:
        insight += (
            f" If this amount earned more than {inflation_rate*100:.2f}% annually, "
            "it could have protected your purchasing power better."
        )

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
    return render_template("calculator.html", current_year=current_year)


def parse_payload(payload):
    description = (payload.get("description", "") or "").strip()

    try:
        initial_amount = float(str(payload.get("initial_amount", "0")).replace(",", ""))
    except (ValueError, TypeError):
        initial_amount = 0.0

    try:
        start_year = int(payload.get("start_year", datetime.now().year))
    except (ValueError, TypeError):
        start_year = datetime.now().year

    try:
        end_year = int(payload.get("end_year", start_year))
    except (ValueError, TypeError):
        end_year = start_year

    manual_rate = payload.get("inflation_rate", "")

    try:
        manual_rate = float(str(manual_rate).strip()) if str(manual_rate).strip() != "" else None
    except (ValueError, TypeError):
        manual_rate = None

    if end_year < start_year:
        end_year = start_year

    if initial_amount < 0:
        initial_amount = 0.0

    return description, initial_amount, start_year, end_year, manual_rate


def run_calculation(payload):
    description, initial_amount, start_year, end_year, manual_rate = parse_payload(payload)
    api_rate_percent = fetch_average_inflation_rate(start_year, end_year)

    if api_rate_percent is not None:
        inflation_rate = api_rate_percent / 100.0
        inflation_source = "World Bank"
    else:
        inflation_rate = (manual_rate / 100.0) if manual_rate is not None else 0.0
        inflation_source = "Manual input"

    result_data = calculate_inflation_regret(initial_amount, start_year, end_year, inflation_rate)

    record = Calculation(
        description=description or "No description provided",
        initial_amount=initial_amount,
        start_year=start_year,
        end_year=end_year,
        inflation_rate=inflation_rate,
        inflation_source=inflation_source,
        future_cost=result_data["future_cost"],
        purchasing_power_loss=result_data["purchasing_power_loss"],
        regret_score=result_data["regret_score"],
        verdict=result_data["verdict"],
        insight=result_data["insight"],
    )
    db.session.add(record)
    db.session.commit()

    projection = build_projection(initial_amount, start_year, end_year, inflation_rate)

    return {
        "id": record.id,
        "description": record.description,
        "initial_amount": initial_amount,
        "start_year": start_year,
        "end_year": end_year,
        "inflation_rate": inflation_rate,
        "inflation_source": inflation_source,
        "projection": projection,
        **result_data,
    }


@app.route("/calculate", methods=["POST"])
def calculate():
    payload = request.get_json(silent=True) if request.is_json else request.form
    data = run_calculation(payload)

    return jsonify(
        {
            "description": data["description"],
            "initial_amount": round(data["initial_amount"], 2),
            "start_year": data["start_year"],
            "end_year": data["end_year"],
            "years": data["years"],
            "inflation_rate": round(data["inflation_rate"] * 100, 2),
            "inflation_source": data["inflation_source"],
            "future_cost": round(data["future_cost"], 2),
            "purchasing_power_loss": round(data["purchasing_power_loss"], 2),
            "regret_score": round(data["regret_score"], 2),
            "insight": data["insight"],
            "verdict": data["verdict"],
            "projection": data["projection"],
        }
    )


@app.route("/result", methods=["POST"])
def result():
    data = run_calculation(request.form)

    return render_template("calculation_result.html", **data)


@app.route("/history", methods=["GET"])
def history():
    search_term = request.args.get("q", "").strip()
    query = Calculation.query

    if search_term:
        query = query.filter(Calculation.description.ilike(f"%{search_term}%"))

    records = query.order_by(Calculation.created_at.desc()).all()
    return render_template("calculation_history.html", records=records, search_term=search_term)


@app.route("/history/<int:record_id>/delete", methods=["POST"])
def delete_history(record_id):
    record = Calculation.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for("history", q=request.args.get("q", "")))


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
