from flask import Flask, jsonify, request, render_template
import requests
from openai_secrets import API_KEY
from openai import OpenAI

openai_client = OpenAI(api_key=API_KEY)

list_level = ["Federal", "State", "District", "All"]
list_inquiry = ["Election Ballot", "Environmental Issues", "Healthcare Issues",
               "Immigration", "Education", "Housing", "Foreign Policy", "Infrastructure", "Taxes"]



app = Flask(__name__)
civic_info_key = 'AIzaSyBdkH1aq-ZlY8UhEEEI7-YfLghVN82N6UY'
base_elections_url = 'https://www.googleapis.com/civicinfo/v2/elections'
base_representatives_url = 'https://www.googleapis.com/civicinfo/v2/representatives'



user_info = {
    "zipcode": 0,
    "policy_interests": ["climate_change", "democracy", "healthcare", "education"]
}

@app.route('/')
def home():
    return render_template('form.html', level = list_level, inquiry = list_inquiry)

@app.route('/user', method=['POST', 'GET'])
def user():
    if request.method == 'POST':
        user_info['zipcode'] = request.form['zipcode']
        user_info['policy_interests'] = request.form['policy_interests']
        return True
    else:
        return render_template('form.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    data = {"message": "Hello, World!"}
    return jsonify(data)


def send_request_to_api():
    zip_code = '10027'
    state = 'NY'
    address = f'1600 Amphitheatre Parkway, Mountain View, {state} {zip_code}'

    params = {
        'key': civic_info_key
    }

    current_year = datetime.now().year
    # get the current year's election info
    elections_response = requests.get(base_elections_url, params=civic_info_key)
    if elections_response.status_code == 200:
        elections_data = response.json()
        elections = elections_data.get('elections', [])

            # Filter elections for the current year
            current_year_elections = [
                election for election in elections
                if election['electionDay'].startswith(str(current_year))
            ]

            print("Upcoming Elections in Current Year:")
            for election in current_year_elections:
                print(f"- {election['name']} on {election['electionDay']}")
        print(data)
    else:
        print(f'Error: {elections_response.status_code}')
        print(elections_response.text)

    # get representative information
    rep_params = {
        'key': civic_info_key,
        'address': address
    }

    rep_response = requests.get(base_representatives_url, params=rep_params)

    if rep_response.status_code == 200:
        rep_data = rep_response.json()
        print("\nRepresentatives:")
        for official in rep_data.get('officials', []):
            print(f"- {official['name']}: {official.get('party', 'No party info')}")
    else:
        print(f'Error fetching representatives: {rep_response.status_code}')
        print(rep_response.text)

    return render_template(results.html, title="Results", current_year_elections=current_year_elections, rep_data=rep_data)

if __name__ == '__main__':
    app.run(debug=True, port=5001)