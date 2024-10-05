from flask import Flask, jsonify, request, render_template
from openai_secrets import API_KEY
from openai import OpenAI

openai_client = OpenAI(api_key=API_KEY)

app = Flask(__name__)



user_info = {
    "zipcode": 0,
    "policy_interests": ["climate_change", "democracy", "healthcare", "education"]
}

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/user', method=['POST', 'GET'])
def user():
    if request.method == 'POST':
        user_info['zipcode'] = request.form['zipcode']
        user_info['policy_interests'] = request.form['policy_interests']
        return True
    else:
        return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)