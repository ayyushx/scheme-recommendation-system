from flask import Flask, render_template, request, send_file
import csv
from io import BytesIO
from xhtml2pdf import pisa

app = Flask(__name__)

# Function to load schemes from the CSV file
def load_schemes(csv_file):
    schemes = []
    try:
        with open(csv_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                schemes.append(row)
    except FileNotFoundError:
        print(f"Error: {csv_file} not found.")
    return schemes

# Function to filter eligible schemes
def filter_schemes(schemes, age, income, employment, residency):
    eligible_schemes = []
    for scheme in schemes:
        try:
            min_age, max_age = map(int, scheme["Age"].split("-"))
            if (
                min_age <= age <= max_age
                and scheme["Income Range"] == income
                and scheme["Employment Status"].lower() == employment.lower()
                and scheme["Residency"].lower() == residency.lower()
            ):
                eligible_schemes.extend(scheme["Eligible Schemes"].split(", "))
        except Exception as e:
            print(f"Error processing scheme: {scheme}, Error: {e}")
    return eligible_schemes

# Function to generate a PDF
def generate_pdf(name, schemes):
    html = render_template("pdf_template.html", name=name, schemes=schemes)
    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf)
    if pisa_status.err:
        print("PDF generation failed.")
        return None
    pdf.seek(0)
    return pdf

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get user inputs
        name = request.form.get("name")
        age = int(request.form.get("age"))
        income = request.form.get("income")
        employment = request.form.get("employment")
        residency = request.form.get("residency")

        # Load schemes
        csv_file = "data/scheme_recommendations.csv"  # Ensure this file exists
        schemes = load_schemes(csv_file)

        # Get eligible schemes
        eligible_schemes = filter_schemes(schemes, age, income, employment, residency)

        # Generate PDF
        pdf = generate_pdf(name, eligible_schemes)
        if pdf:
            return send_file(
                pdf,
                as_attachment=True,
                download_name=f"{name}_eligible_schemes.pdf",
                mimetype="application/pdf",
            )

        # Fallback if PDF generation fails
        return render_template("result.html", name=name, schemes=eligible_schemes)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
