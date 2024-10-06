import datetime
import requests
from flask import Flask, request, render_template
from api_secrets import MAPS_API_KEY, CIVIC_INFO_API_KEY

list_level = ["Federal", "State", "District", "Local"]
list_inquiry = ["Climate Change", "Healthcare", "Immigration", "Education",
                "Housing", "Foreign Policy", "Infrastructure", "Economy",
                "Criminal Justice", "Guns", "Reproductive Health"]

app = Flask(__name__)
base_elections_url = 'https://www.googleapis.com/civicinfo/v2/elections'
base_representatives_url = 'https://www.googleapis.com/civicinfo/v2/representatives'


@app.route('/')
def home():
    """Render the form on the homepage."""
    return render_template('form.html', maps_api_key=MAPS_API_KEY, level=list_level, inquiry=list_inquiry)


@app.route('/results', methods=['GET'])
def show_results():
    # # Get the form data
    # street_address = request.form.get('address')
    # selected_levels = request.form.getlist('level')  # Multiple selections
    # selected_inquiries = request.form.getlist('inquiry')  # Multiple selections
    #
    # # This is just placeholder data; in reality, you'd use real data from API
    # info = [
    #     {'name': 'ava', 'platform': [{'issue': 'Climate Change', 'policy': ''}, {'issue': '', 'policy': ''}]},
    #     {'name': 'pru', 'platform': [{'issue': 'Healthcare', 'policy': ''}]}
    # ]

    # Pass the form data and results to the results template
    return render_template('results.html')


def get_elections(address: str):
    """Fetch elections and representatives based on address."""
    params = {'key': CIVIC_INFO_API_KEY}

    # Get the current year's election info
    elections_response = requests.get(base_elections_url, params=params)
    if elections_response.status_code == 200:
        elections_data = elections_response.json()
        elections = elections_data.get('elections', [])
        current_year = datetime.datetime.now().year

        # Filter elections for the current year
        current_year_elections = [
            election for election in elections
            if election['electionDay'].startswith(str(current_year))
        ]
    else:
        current_year_elections = []

    # Fetch representative data
    rep_params = {'key': CIVIC_INFO_API_KEY, 'address': address}
    rep_response = requests.get(base_representatives_url, params=rep_params)

    if rep_response.status_code == 200:
        rep_data = rep_response.json()
    else:
        rep_data = {}

    return current_year_elections, rep_data


if __name__ == '__main__':
    app.run(debug=True, port=5001)
