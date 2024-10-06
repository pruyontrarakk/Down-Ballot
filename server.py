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
    global policy_results
    if request.method == 'POST':
        session['street_address'] = request.form.get('address')
        session['selected_levels'] = request.form.getlist('level')
        session['selected_inquiries'] = request.form.getlist('inquiry')

        # Fetch the election data
        current_year_elections, rep_data = get_elections(session['street_address'])

        # prepare the candidate array for gpt
        candidate_array = [
            {
                'name': rep['name'],
                'party': rep['party'],
                'phones': rep['phones'],
                'c_platform': [{'issue': iss_name, 'policy': ''} for iss_name in session['selected_inquiries']]
            }
            for rep in rep_data['officials']
        ]
        policy_results = get_policy_from_gpt(candidate_array, OPENAI_API_KEY)
        # Store data in session

        session['current_year_elections'] = current_year_elections
        return redirect(url_for('show_results'))

    elif request.method == 'GET':
        # Handle the GET request separately here
        current_year_elections = session.get('current_year_elections', [])
        # rep_data = session.get('rep_data', {})
        print(policy_results)
        return render_template(
            'results.html',
            representatives=policy_results,
            current_year_elections=current_year_elections
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


def get_policy_from_gpt(candidate_array, openai_api_key):
    try:
        headers = {
            'Authorization': f'Bearer {openai_api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            "model": "gpt-4o",  # Replace with the model you want to use
            "messages": [
                {
                    "role": "user",
                    "content": f"Here's an array of candidates for the 2024 election. For each issue, fill in the "
                               f"policy field with 1-2 sentence summary of the candidate's position on that issue. The"
                               f" array is: {json.dumps(candidate_array, indent=2)}. The output needs to match the "
                               f"input (raw, stringified JSON) except with the policy field filled in for each issue. "
                               f"No need to mark the response as json via backticks! just return the stringified JSON."
                },
                {
                    "role": "system",
                    "content": "You are trying to help someone understand the policy positions of the candidates in "
                               "their local elections. Keep answers minimal and informative."
                }
            ],
            "temperature": 0.4
        }

        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for HTTP errors

        response_data = response.json()

        return json.loads(response_data['choices'][0]['message']['content'])
    except requests.exceptions.RequestException as e:
        print(f'Error with OpenAI request: {e}')
        return


if __name__ == '__main__':
    app.run(debug=True, port=5001)
