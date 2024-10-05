import datetime

import requests
from flask import Flask, request, render_template, jsonify
from openai import OpenAI

from api_secrets import OPENAI_API_KEY, MAPS_API_KEY, CIVIC_INFO_API_KEY

openai_client = OpenAI(api_key=OPENAI_API_KEY)

list_level = ["Federal", "State", "District", "Local"]
list_inquiry = ["Climate Change", "Healthcare",
                "Immigration", "Education", "Housing", "Foreign Policy",
                "Infrastructure", "Economy", "Criminal Justice", "Guns", "Reproductive Health"]

app = Flask(__name__)
base_elections_url = 'https://www.googleapis.com/civicinfo/v2/elections'
base_representatives_url = 'https://www.googleapis.com/civicinfo/v2/representatives'

user_info = {
    "address": None,
    "policy_choices": None,
    "level_choices": None
}


@app.route('/')
def home():
    return render_template('form.html', maps_api_key=MAPS_API_KEY, level=list_level, inquiry=list_inquiry)


@app.route('/user', methods=['POST', 'GET'])
def user():
    global user_info
    if request.method == 'POST':
        user_info['address'] = request.form['address']
        user_info['level_choices'] = request.form['level_choices']
        user_info['policy_choices'] = request.form['policy_choices']
        current_year_elections, rep_data = get_elections(user_info['address'])
        print(user_info)
        return jsonify({"elections": current_year_elections, "representatives": rep_data})
    else:
        return render_template('form.html')


def get_elections(address: str, levels: list[str]):
    params = {
        'key': CIVIC_INFO_API_KEY
    }

    current_year = datetime.datetime.now().year
    # get the current year's election info
    elections_response = requests.get(base_elections_url, params=params)
    if elections_response.status_code == 200:
        elections_data = elections_response.json()
        elections = elections_data.get('elections', [])

        # Filter elections for the current year
        current_year_elections = [
            election for election in elections
            if election['electionDay'].startswith(str(current_year))
        ]

        print("Upcoming Elections in Current Year:")
        for election in current_year_elections:
            print(f"- {election['name']} on {election['electionDay']}")
    else:
        print(f'Error: {elections_response.status_code}')
        print(elections_response.text)
        current_year_elections = None

    # get representative information
    rep_params = {
        'key': CIVIC_INFO_API_KEY,
        'address': address
    }

    rep_response = requests.get(base_representatives_url, params=rep_params)

    if rep_response.status_code == 200:
        rep_data = rep_response.json()
        # print("\nRepresentatives:")
        # for official in rep_data.get('officials', []):
        #     print(f"- {official['name']}: {official.get('party', 'No party info')}")
    else:
        print(f'Error fetching representatives: {rep_response.status_code}')
        print(rep_response.text)
        rep_data = None

    return current_year_elections, rep_data


if __name__ == '__main__':
    app.run(debug=True, port=5001)
