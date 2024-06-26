import requests
from flask import Flask, jsonify, request, render_template, url_for, flash, session, make_response
from bs4 import BeautifulSoup
import secrets
from tools import calories as cl, Bmi, api
from tools import data
from waitress import serve

app = Flask(__name__)
app.config['SECRET_KEY'] = 'something-secret...haha'
activeclass = 1

# ------------------------Muscles----------------------

lstofmuscles = ["Biceps", "Forearms", "Shoulders", "Triceps", "Quads", "Glutes", "Lats", "Lower back",
                "Hamstrings", "Chest", "Abdominals", "Obliques", "Traps", "Calves"]
lstofequipments = ['Barbell', 'Dumbbells', 'Bodyweight', 'Machine', 'Medicine-Ball', 'Kettlebells', 
'Stretches', 'Cables', 'Band', 'Plate', 'TRX', 'Yoga', 'Bosu', 'Bosu-Ball', 'Cardio', 'Smith-Machine']


# --------------------------Functions for specific Tasks----------------------

def bard(data):
    
    key="secretcantbeleaked"
    url = f"https://generativelanguage.googleapis.com/v1beta2/models/text-bison-001:generateText?key={key}"
    headers = {"Content-Type": "application/json"}
     
    data = {"prompt": {"text": f"My height is {data.get('height')}cm, current weight is {data.get('weight')}kg, gender is {data.get('gender')}, activity level is {data.get('activity_level')}, age is {data.get('age')} and want to {data.get('goal')} weight so prepare a Detailed diet chart for me. Don't give me calories intake or macronutrients"}}
    response = requests.post(url, headers=headers, json=data)
    return dict(response.json()).get('candidates')[0].get('output') #read about webhooks in python flask

# ------------------------------------------------------


# ------------------------Routes-----------------------

@app.route("/")
def home():
    return render_template('home.html', page="home", activeclass="home")

@app.route("/begins", methods=['GET', 'POST'])
def forms():
    imglink = url_for('static', filename="bgstarted.jpg")
    session['key']=secrets.token_hex(32)
    if request.method == 'POST':
        equipment = request.form.get('equipment')
        muscle = request.form.get('muscle')

        #-----------------------new edit -------------------------------
        if data.muscles.get(muscle) != None and data.equipments.get(equipment)!=None:
            results = api.get_exercise(muscle=str(data.muscles.get(muscle)['id']), category=str(data.equipments.get(equipment)['id']))
            return render_template('exercise.html', page="exercise", results = results)
        
        flash('Oops! No exercise found. Please try again with different filters', "red")
        return render_template('forms.html', page="forms", activeclass="forms", imglink=imglink,
            lstofmuscles=lstofmuscles,
            lstofequipments=lstofequipments)
        
        return render_template('forms.html', page="forms", activeclass="forms", imglink=imglink,
                               lstofmuscles=lstofmuscles, lstofequipments=lstofequipments, key=session['key'])
        #---------------------------------------------------------------
        if len(results) == 0:
            flash('Oops! No exercise found. Please try again with different filters', "red")
            return render_template('forms.html', page="forms", activeclass="forms", imglink=imglink,
                                   lstofmuscles=lstofmuscles,
                                   lstofequipments=lstofequipments, )
        return render_template('resultlist.html', results=results)
    else:
        session['key']=secrets.token_hex(32)
        return render_template('forms.html', page="forms", activeclass="forms", imglink=imglink,
                               lstofmuscles=lstofmuscles, lstofequipments=lstofequipments, key=session['key'])

@app.route("/exercise/<slug>")
def exercise(slug):
    url = "link"
    payload={"slug": slug}
    res = requests.get(url=url, params=payload)
    res = res.json()
    result = {}
    if res.get("results")!=None and len(res.get("results")) > 0:
        result = {
            "difficulty": res.get("results")[0].get("difficulty"),
            "correct_steps": res.get("results")[0].get("correct_steps"),
            "content": api.video(res.get("results")[0].get("name"))
        }
        return make_response(jsonify({"status":1, 'result': result}), 200)
        
        
    else :
        return make_response(jsonify({"status":0, 'result': {}}), 400)

@app.route("/prepare", methods=['POST'])
def prepare():
    data=request.get_json()
    data = dict(data)
    received_key = request.headers.get('X-Auth-Key')
    session_key = session.get('key')
    cookie_session=str(request.headers.get('Cookie'))
    cookie_session = cookie_session[:8:]
    if received_key != session_key :
        return jsonify({'error': 'Unauthorized'}), 401
    if data.get('height')==None:
        return jsonify({'diet-chart'+received_key: "Fill all the values and submit then try again"})
    chart = str(bard(data))
    j=0
    for i in range(len(chart)):
        if chart[i]=='*':
            j=i
            break
    chart=chart[j::1]
    chart=chart.replace('\n', '<br>')
    chart=chart.replace("**", "1. ", 1)
    chart=chart.replace("**", "", 1)
    chart=chart.replace("**", "2. ", 1)
    chart=chart.replace("**", "", 1)
    chart=chart.replace("**", "3. ", 1)
    chart=chart.replace("**", "", 1)
    chart=chart.replace("**", "4. ", 1)
    chart=chart.replace("**", "", 1)
    return jsonify({'diet-chart'+received_key: chart})
    
@app.route("/calculate", methods=['POST'])
def calculate():
    data = request.get_json()
    received_key = request.headers.get('X-Auth-Key')
    session_key = session.get('key') 
    cookie_session=str(request.headers.get('Cookie'))
    cookie_session = cookie_session[:8:]
    if received_key != session_key :
        return jsonify({'error': 'Unauthorized'}), 401
    data = dict(data)
    bmi = Bmi.calculate_bmi_with_info(data['weight'], data['height'] / 100, "en")
    calories = cl.calculate_calorie_needs(age=data.get('age'), weight=data.get('weight'),
                                          target_weight=data.get('target_weight'),
                                          height=data.get('height'), time_frame=data.get('time frame'),
                                          activity_level=data.get('activity_level'), goal=data.get('goal'),
                                          gender=data.get('gender'))
    macros = cl.macro_needs(age=data.get('age'), weight=data.get('weight'),
                                          target_weight=data.get('target_weight'),
                                          height=data.get('height'), time_frame=data.get('time frame'),
                                          activity_level=data.get('activity_level'), goal=data.get('goal'),
                                          gender=data.get('gender'))
    result = {
        'bmi': "{:.2f}".format(bmi[0]),
        'category': bmi[1],
        'calories': int(calories),
        'target_weight': data.get('target_weight'),
        'carb': macros.get('carbs'),
        'fat': macros.get('fat'),
        'protein': macros.get('protein'),
        'carb_per': macros['carb_per'],
        'protein_per': macros.get('protein_per'),
        'fat_per': macros.get('fat_per')
    }
    return jsonify(result)

@app.route("/about")
def about():
    return render_template('about.html', page="about", activeclass="about")


if __name__ == '__main__':

    serve(app,
        host='0.0.0.0',
        port=8080,
        threads=10,
        channel_timeout=300,
        backlog=600
    )
