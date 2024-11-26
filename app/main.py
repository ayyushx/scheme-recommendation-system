from flask import Flask, render_template, request
import csv

app = Flask(__name__)

# Function to load schemes from the CSV file
def load_schemes(csv_file):
    schemes = []
    with open(csv_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            schemes.append(row)
    return schemes

# Function to filter eligible schemes
def filter_schemes(schemes, age, income, employment, residency):
    eligible_schemes = []
    for scheme in schemes:
        try:
            # Split the "Age" range field and check if the user's age falls in the range
            min_age, max_age = map(int, scheme["Age"].split("-"))
            if (
                min_age <= age <= max_age and
                scheme["Income Range"] == income and
                scheme["Employment Status"].lower() == employment.lower() and
                scheme["Residency"].lower() == residency.lower()
            ):
                eligible_schemes.append(scheme["Eligible Schemes"])
        except Exception as e:
            print(f"Error processing scheme: {scheme}, Error: {e}")
    return eligible_schemes

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get user inputs
        name = request.form["name"]
        age = int(request.form["age"])
        income = request.form["income"]
        employment = request.form["employment"]
        residency = request.form["residency"]

        # Load schemes
        csv_file = "data/scheme_recommendations.csv"
        schemes = load_schemes(csv_file)

        # Get eligible schemes
        eligible_schemes = filter_schemes(schemes, age, income, employment, residency)

        # Render result page
        return render_template("result.html", name=name, schemes=eligible_schemes)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
