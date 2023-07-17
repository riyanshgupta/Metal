import requests
from flask import Flask, jsonify, request, render_template, url_for, flash, session
import secrets
from tools import calories as cl, Bmi
from waitress import serve
import pprint
import google.generativeai as palm
app = Flask(__name__)
app.config['SECRET_KEY'] = 'making-flask'
activeclass = 1

# ------------------------Muscles----------------------

lstofmuscles = ["Biceps", "Forearms", "Shoulders", "Triceps", "Quads", "Glutes", "Lats", "Mid back", "Lower back",
                "Hamstrings", "Chest", "Abdominals", "Obliques", "Traps", "Calves"]
lstofequipments = ["Barbell", "Dumbbells", "Kettlebells", "Stretches", "Cables", "Band", "Plate", "TRX", "Bodyweight",
                   "Yoga", "Machine"]



# --------------------------Functions for specific Tasks----------------------

def getexercisebycategory(muscle, equipment, level):
    url = "https://musclewiki.p.rapidapi.com/exercises"
    querystring = {"muscle": str(muscle), "category": str(equipment), "difficulty": str(level)}
    headers = {
        "X-RapidAPI-Key": "089f1639cbmshb14fba280fadcb9p1edbf9jsn400b252ef620",
        "X-RapidAPI-Host": "musclewiki.p.rapidapi.com"
    }

    response = (requests.request("GET", url, headers=headers, params=querystring)).json()
    result = response
    return result

def bard(data):
    key="AIzaSyCxa5DEoAezgHi6POcFvDeRoBxPWfHrN6Y"
    palm.configure(api_key=key)
    models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
    model = models[0].name
    prompt = f""" My height is {data.get('height')}cm, current weight is {data.get('weight')}kg, gender is {data.get('gender')}, activity level is {data.get('activity_level')}, age is {data.get('age')} and want to {data.get('goal')} weight so prepare a Detailed diet chart for me. Don't give me number of calories or Macronutrients"""
    completion = palm.generate_text(
        model=model,
        prompt=prompt,
        temperature=0,
        max_output_tokens=1200,
    )
    return completion.result #read about webhooks in python flask

# ------------------------------------------------------


# ------------------------Routes-----------------------

@app.route("/")
def home():
    return render_template('home.html', page="home", activeclass="home")

@app.route("/begins", methods=['GET', 'POST'])
def forms():
    imglink = url_for('static', filename="bgstarted.jpg")
    if request.method == 'POST':
        level = request.form.get('level')
        equipment = request.form.get('equipment')
        muscle = request.form.get('muscle')
        results = getexercisebycategory(muscle, equipment, level)
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

@app.route("/prepare", methods=['POST'])
def prepare():
    data=request.get_json()
    data = dict(data)
    received_key = request.headers.get('X-Auth-Key')
    session_key = session.get('key')
    cookie_session=str(request.headers.get('Cookie'))
    cookie_session = cookie_session[:8:]
    if received_key != session_key or received_key==None or cookie_session!='session=':
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
    chart=chart.replace("**", "5. ", 1)
    chart=chart.replace("**", "", 1)
    chart=chart.replace("**", "6. ", 1)
    chart=chart.replace("**", "", 1)
    chart = chart.replace('*', "")
    return jsonify({'diet-chart'+received_key: chart})
    
@app.route("/calculate", methods=['POST'])
def calculate():
    data = request.get_json()
    received_key = request.headers.get('X-Auth-Key')
    session_key = session.get('key')
    cookie_session=str(request.headers.get('Cookie'))
    cookie_session = cookie_session[:8:]
    if received_key != session_key or received_key==None or cookie_session!='session=':
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
    # with app.app_context():
    #     app.run(port=5000, debug=False)
    serve(app,
        host='0.0.0.0',
        port=8080,
        threads=10,
        channel_timeout=300,
        backlog=600
    )