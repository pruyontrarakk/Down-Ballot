import datetime
import json
import os
import requests
from flask import Flask, session, redirect, url_for, request, render_template
from api_secrets import MAPS_API_KEY, CIVIC_INFO_API_KEY, OPENAI_API_KEY

list_level = ["Federal", "State", "District", "Local"]
list_inquiry = ["Climate Change", "Healthcare", "Immigration", "Education",
                "Housing", "Foreign Policy", "Infrastructure", "Economy",
                "Criminal Justice", "Guns", "Reproductive Health"]

policy_results = []
app = Flask(__name__)

base_elections_url = 'https://www.googleapis.com/civicinfo/v2/elections'
base_representatives_url = 'https://www.googleapis.com/civicinfo/v2/representatives'
app.config['SECRET_KEY'] = os.urandom(24)

@app.route('/')
def home():
    """Render the form on the homepage."""
    return render_template('form.html', maps_api_key=MAPS_API_KEY, openai_api_key=OPENAI_API_KEY, level=list_level, inquiry=list_inquiry)


@app.route('/results', methods=['POST', 'GET'])
def show_results():
    if request.method == 'POST':
        session['street_address'] = request.form.get('address')
        session['selected_levels'] = request.form.getlist('level')
        session['selected_inquiries'] = request.form.getlist('inquiry')

        # Fetch the election data
        current_year_elections, rep_data = get_elections(session['street_address'])

        # Store data in session
        session['current_year_elections'] = current_year_elections
        session['rep_data'] = rep_data['officials']
        print(session['rep_data'])

        # Redirect to the GET route
        return redirect(url_for('show_results'))

    elif request.method == 'GET':
        # Handle the GET request separately here
        current_year_elections = session.get('current_year_elections', [])
        rep_data = session.get('rep_data', {})
        representatives=extract_representative_data(rep_data)

        return render_template(
            'results.html',
            current_year_elections=current_year_elections,
            representatives = representatives
        )

def extract_representative_data(rep_data):
    representatives = []

    for rep in rep_data:
        representative_info = {
            'name': rep.get('name', 'N/A'),
            'party': rep.get('party', 'N/A'),
            'phones': ', '.join(rep.get('phones', ['N/A'])),
            'urls': ', '.join(rep.get('urls', ['N/A']))
        }
        representatives.append(representative_info)

    return representatives


@app.route("/post_results", methods=['POST'])
def post_results():
    global policy_results
    policy_results = request.get_json()
    return policy_results

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
        # for office in rep_data.get('offices', []):
        #     print(f"- {office['name']}: {office.get('roles', 'No role info')}, {office.get('urls')}")
    else:
        rep_data = {}

    return current_year_elections, rep_data


if __name__ == '__main__':
    app.run(debug=True, port=5001)
