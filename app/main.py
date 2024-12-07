from flask import Flask, render_template, request, send_file
import csv
import os
from io import BytesIO
from xhtml2pdf import pisa

app = Flask(__name__)


# Function to load schemes from the CSV file
def load_schemes(csv_file):
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file '{csv_file}' not found.")

    schemes = []
    with open(csv_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        schemes = [row for row in reader]
    return schemes


# Function to filter eligible schemes
def filter_schemes(schemes, age, income, employment, residency):
    eligible_schemes = []
    for scheme in schemes:
        try:
            min_age, max_age = map(int, scheme["Age"].split("-"))
            if (
                    min_age <= age <= max_age
                    and scheme["Income Range"].lower() == income.lower()
                    and scheme["Employment Status"].lower() == employment.lower()
                    and scheme["Residency"].lower() == residency.lower()
            ):
                eligible_schemes.extend(scheme["Eligible Schemes"].split(", "))
        except ValueError as ve:
            print(f"Value error processing scheme: {scheme}. Error: {ve}")
        except KeyError as ke:
            print(f"Key error in scheme data: Missing key {ke}")
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
    try:
        if request.method == "POST":
            # Get user inputs
            name = request.form.get("name", "User").strip()
            age = int(request.form.get("age", 0))
            income = request.form.get("income", "").strip()
            employment = request.form.get("employment", "").strip()
            residency = request.form.get("residency", "").strip()

            # Validate inputs
            if not (name and income and employment and residency and age > 0):
                return render_template("index.html", error="All fields are required and age must be positive.")

            # Load schemes
            csv_file = os.path.join("data", "scheme_recommendations.csv")
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

    except Exception as e:
        print(f"Error: {e}")
        return render_template("index.html", error="An unexpected error occurred. Please try again.")


if __name__ == "__main__":
    app.run(debug=True)
