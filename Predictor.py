#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask, request, render_template_string
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import io
import base64

# Load Calories Burned Prediction model
model = joblib.load("prediction_utils/calories_burned_model.pkl")
feature_cols = joblib.load("prediction_utils/feature_columns.pkl")
encoders = {col: joblib.load(f"prediction_utils/{col}_encoder.pkl") for col in ["BMI_Category", "Fitness_Level"]}

# Load macronutrient model and encoders
macros_model = joblib.load("prediction_utils/macros_model.pkl")
macros_features = joblib.load("prediction_utils/macros_feature_columns.pkl")  # <-- Fixed this line
macro_encoders = {
    col: joblib.load(f"prediction_utils/{col}_encoder.pkl")
    for col in ["Meal_Type", "Diet_Type", "BMI_Category"]
}

# Flask setup
app = Flask(__name__)


# In[ ]:


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ page_title }}</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
            color: #fff;
        }
        .sidebar {
            height: 100vh;
            width: 240px;
            position: fixed;
            background-color: #111;
            padding-top: 30px;
        }
        .sidebar a {
            padding: 15px 25px;
            text-decoration: none;
            font-size: 18px;
            color: #ccc;
            display: block;
        }
        .sidebar a:hover {
            background-color: #575757;
        }
        .main {
            margin-left: 260px;
            padding: 20px;
        }
        .app-name {
            font-family: 'Trebuchet MS', sans-serif;
            font-size: 26px;
            color: #ffcc00;
            margin-bottom: 10px;
        }
        h1 {
            color: #00ffcc;
            margin-top: 0;
        }
        form {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            max-width: 600px;
        }
        label {
            display: block;
            margin-top: 15px;
        }
        select, input, button {
            width: 100%;
            padding: 10px;
            margin-top: 10px;
            border-radius: 8px;
            border: none;
            font-size: 16px;
        }
        button {
            background-color: #00cc99;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover {
            background-color: #00b386;
        }
        .result {
            margin-top: 20px;
            font-size: 18px;
            background: rgba(0,0,0,0.5);
            padding: 15px;
            border-radius: 10px;
            color: #00ffcc;
        }
        .error {
            margin-top: 20px;
            font-size: 16px;
            color: red;
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 10px;
        }
        .footer {
            margin-top: 50px;
            font-size: 14px;
            color: #ccc;
            text-align: center;
        }
        .footer a {
            color: #ccc;
            text-decoration: none;
        }
        .footer a:hover {
            color: #00ffcc;
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <a href="/">Calories Burned Prediction</a>
        <a href="/macros">Macronutrient Distribution</a>
        <a href="/exercise">Exercise Duration Suggestion</a>
        <a href="/more">More</a>
    </div>

    <div class="main">
        <div class="app-name">Personalized Health & Fitness AI Suite</div>
        <h1>{{ heading }}</h1>
        {{ content | safe }}
        <div class="footer">
            <hr>
            <div><strong>Developed by Tejas Jain</strong> | B.Tech CSE (Data Science), Poornima Institute of Engineering and Technology, Jaipur</div>
            <div>
                📧 <a href="mailto:2022pietcdtejas056@poornima.org">2022pietcdtejas056@poornima.org</a> |
                🔗 <a href="http://www.linkedin.com/in/tejas-jain-44a001261" target="_blank">LinkedIn</a> |
                💻 <a href="https://github.com/056tejas" target="_blank">GitHub</a>
            </div>
        </div>
    </div>
</body>
</html>
"""


# In[ ]:


@app.route("/", methods=["GET", "POST"])
def predict_calories():
    prediction = None
    error = None
    summary = None
    result_html = ""

    durations = [round(i / 20, 2) for i in range(1, 21)]
    heart_rates = [round(i / 20, 2) for i in range(1, 21)]

    intensity_options = "".join([f'<option value="{i}">{i}</option>' for i in range(1, 11)])
    duration_options = "".join([f'<option value="{val}">{val}</option>' for val in durations])
    heart_rate_options = "".join([f'<option value="{val}">{val}</option>' for val in heart_rates])

    if request.method == "POST":
        try:
            data = {col: request.form[col] for col in feature_cols}
            input_data = []

            for col in feature_cols:
                if col in encoders:
                    val = encoders[col].transform([data[col]])[0]
                else:
                    val = float(data[col])
                input_data.append(val)

            prediction = round(model.predict([input_data])[0], 2)

            # Add an interpreted summary based on predicted value
            if prediction < 0.2:
                summary = "Very low calorie burn — consider increasing exercise intensity or duration."
            elif prediction < 0.5:
                summary = "Moderate calorie burn — suitable for light workouts or warmups."
            elif prediction < 0.8:
                summary = "High calorie burn — ideal for improving stamina and fitness."
            else:
                summary = "Very high calorie burn — excellent for intense fat-burning workouts."

        except Exception:
            error = "Invalid input. Please check your values."

    form_html = f"""
        <form method="POST">
            <label>Exercise Intensity (1–10):</label>
            <select name="Exercise Intensity" required>{intensity_options}</select>

            <label>Duration (0 to 1):</label>
            <select name="Duration">{duration_options}</select>

            <label>Heart Rate (0 to 1):</label>
            <select name="Heart Rate">{heart_rate_options}</select>

            <label>BMI Category:</label>
            <select name="BMI_Category" required>
                <option value="Underweight">Underweight</option>
                <option value="Normal">Normal</option>
                <option value="Overweight">Overweight</option>
                <option value="Obese">Obese</option>
            </select>

            <label>Fitness Level:</label>
            <select name="Fitness_Level" required>
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
            </select>

            <button type="submit">Predict</button>
        </form>
    """

    if prediction is not None:
        result_html = f"<div class='result'>Predicted Calories Burned: <strong>{prediction}</strong>"
        if summary:
            result_html += f"<p style='margin-top:10px; font-style: italic; color: #ffcc99;'>{summary}</p>"
        result_html += "</div>"

    if error:
        form_html += f"<div class='error'>{error}</div>"

    return render_template_string(
        HTML_TEMPLATE,
        page_title="Calories Burned | Health & Fitness AI",
        heading="Calories Burned Prediction",
        content=form_html + result_html
    )


# In[ ]:


@app.route("/macros", methods=["GET", "POST"])
def predict_macros():
    prediction = None
    chart_base64 = None
    error = None

    form_html = """
    <form method="POST">
        <label>Calories (kcal):</label>
        <input type="number" name="Calories (kcal)" step="0.01" required>

        <label>Meal Type:</label>
        <select name="Meal_Type">
            <option value="Breakfast">Breakfast</option>
            <option value="Lunch">Lunch</option>
            <option value="Dinner">Dinner</option>
            <option value="Snack">Snack</option>
        </select>

        <label>Diet Type:</label>
        <select name="Diet_Type">
            <option value="Balanced">Balanced</option>
            <option value="Low-Carb">Low-Carb</option>
            <option value="High-Protein">High-Protein</option>
            <option value="Vegan">Vegan</option>
        </select>

        <label>BMI Category:</label>
        <select name="BMI_Category">
            <option value="Underweight">Underweight</option>
            <option value="Normal">Normal</option>
            <option value="Overweight">Overweight</option>
            <option value="Obese">Obese</option>
        </select>

        <button type="submit">Predict</button>
    </form>
    """

    if request.method == "POST":
        try:
            cal = float(request.form["Calories (kcal)"])
            meal = request.form["Meal_Type"]
            diet = request.form["Diet_Type"]
            bmi_cat = request.form["BMI_Category"]

            encoded = [
                cal,
                macro_encoders["Meal_Type"].transform([meal])[0],
                macro_encoders["Diet_Type"].transform([diet])[0],
                macro_encoders["BMI_Category"].transform([bmi_cat])[0],
            ]

            output = macros_model.predict([encoded])[0]
            prediction = {
                "Protein (g)": round(output[0], 2),
                "Carbohydrates (g)": round(output[1], 2),
                "Fat (g)": round(output[2], 2),
            }

            # Add an interpreted summary
            main_macro = max(prediction, key=prediction.get)
            summary = f"This meal is primarily composed of {main_macro.lower()}, making it suitable for those needing higher {main_macro.lower()} intake."

            # Create donut chart
            labels = list(prediction.keys())
            values = list(prediction.values())
            fig, ax = plt.subplots(figsize=(6, 6), facecolor='none')
            colors = ['#00cc99', '#00bfff', '#ff9966']
            wedges, texts, autotexts = ax.pie(
                values, labels=labels, autopct='%1.1f%%', startangle=90,
                colors=colors, textprops={'color': 'white', 'fontsize': 12},
                wedgeprops={'edgecolor': 'white'}
            )
            centre_circle = plt.Circle((0, 0), 0.60, fc='black')
            fig.gca().add_artist(centre_circle)
            ax.axis('equal')
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
            buf.seek(0)
            chart_base64 = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()

        except Exception:
            error = "Invalid input. Please check your values."

    result_html = ""
    if prediction:
        result_html += "<div class='result'><h2>Predicted Macronutrient Breakdown:</h2><ul>"
        for k, v in prediction.items():
            result_html += f"<li><strong>{k}:</strong> {v}</li>"
        result_html += "</ul>"

        # Summary line
        main_macro = max(prediction, key=prediction.get)
        summary = f"This meal is primarily composed of {main_macro.lower()}, making it suitable for those needing higher {main_macro.lower()} intake."
        result_html += f"<p style='margin-top:10px; font-style: italic; color: #ffcc99;'>{summary}</p>"

        # Add chart
        result_html += f'<img src="data:image/png;base64,{chart_base64}" alt="Macronutrient Chart" style="margin-top: 10px;" />'
        result_html += "</div>"

    if error:
        result_html += f"<div class='error'>{error}</div>"

    return render_template_string(
        HTML_TEMPLATE,
        page_title="Macronutrient Prediction | Health & Fitness AI",
        heading="Macronutrient Distribution Prediction",
        content=form_html + result_html
    )


# In[ ]:


@app.route("/exercise", methods=["GET", "POST"])
def suggest_exercise():
    suggestion = None
    chart_base64 = None
    tip = None
    error = None

    bmi_options = ["Underweight", "Normal", "Overweight", "Obese"]
    fitness_levels = ["Beginner", "Intermediate", "Advanced"]
    workout_types = ["Cardio", "Strength", "Flexibility", "HIIT"]
    goals = ["Weight Loss", "Muscle Gain", "Flexibility", "General Fitness"]
    genders = ["Male", "Female", "Other"]
    times = list(range(15, 100, 15))

    form_html = """
    <form method="POST">
        <label>BMI Category:</label>
        <select name="BMI_Category">""" + "".join([f"<option value='{opt}'>{opt}</option>" for opt in bmi_options]) + """</select>

        <label>Fitness Level:</label>
        <select name="Fitness_Level">""" + "".join([f"<option value='{opt}'>{opt}</option>" for opt in fitness_levels]) + """</select>

        <label>Workout Preference:</label>
        <select name="Workout_Preference">""" + "".join([f"<option value='{opt}'>{opt}</option>" for opt in workout_types]) + """</select>

        <label>Time Available (minutes):</label>
        <select name="Time">""" + "".join([f"<option value='{t}'>{t}</option>" for t in times]) + """</select>

        <label>Fitness Goal:</label>
        <select name="Goal">""" + "".join([f"<option value='{g}'>{g}</option>" for g in goals]) + """</select>

        <label>Gender:</label>
        <select name="Gender">""" + "".join([f"<option value='{g}'>{g}</option>" for g in genders]) + """</select>

        <button type="submit">Get Suggestion</button>
    </form>
    """

    if request.method == "POST":
        try:
            bmi = request.form["BMI_Category"]
            fitness = request.form["Fitness_Level"]
            workout_pref = request.form["Workout_Preference"]
            time = int(request.form["Time"])
            goal = request.form["Goal"]
            gender = request.form["Gender"]

            # Rule-based suggestions
            if goal == "Weight Loss":
                suggestion = {
                    "Cardio": round(time * 0.5, 1),
                    "HIIT": round(time * 0.3, 1),
                    "Strength": round(time * 0.2, 1),
                }
                tip = "Stay hydrated and focus on consistency. Mix HIIT with light cardio for max burn."

            elif goal == "Muscle Gain":
                suggestion = {
                    "Strength": round(time * 0.6, 1),
                    "HIIT": round(time * 0.2, 1),
                    "Flexibility": round(time * 0.2, 1),
                }
                tip = "Progressive overload is key. Ensure proper protein intake post-workout."

            elif goal == "Flexibility":
                suggestion = {
                    "Flexibility": round(time * 0.6, 1),
                    "Cardio": round(time * 0.3, 1),
                    "Strength": round(time * 0.1, 1),
                }
                tip = "Stretch daily. Focus on breathwork to enhance flexibility routines."

            else:  # General Fitness
                suggestion = {
                    "Cardio": round(time * 0.35, 1),
                    "Strength": round(time * 0.35, 1),
                    "Flexibility": round(time * 0.2, 1),
                    "HIIT": round(time * 0.1, 1),
                }
                tip = "A balanced routine with rest days ensures sustainable progress."

            # Create bar chart
            fig, ax = plt.subplots(figsize=(6, 4), facecolor='none')
            ax.bar(suggestion.keys(), suggestion.values(), color='#ff6666')
            ax.set_title("Workout Time Distribution", color='white')
            ax.set_xlabel("Exercise Type", color='white')
            ax.set_ylabel("Duration (min)", color='white')
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
            buf.seek(0)
            chart_base64 = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()

        except Exception as e:
            error = "Something went wrong. Please check your input values."

    result_html = ""
    if suggestion:
        result_html += "<div class='result'><h2>Recommended Exercise Plan:</h2><ul>"
        for k, v in suggestion.items():
            result_html += f"<li><strong>{k}:</strong> {v} min</li>"
        result_html += "</ul>"

        if tip:
            result_html += f"<p style='margin-top:10px; font-style: italic; color: #ffd699;'>{tip}</p>"

        if chart_base64:
            result_html += f'<img src="data:image/png;base64,{chart_base64}" alt="Workout Chart" style="margin-top: 15px;" />'

        result_html += "</div>"

    if error:
        form_html += f"<div class='error' style='color: #ff9999; margin-top: 20px;'>{error}</div>"

    return render_template_string(
        HTML_TEMPLATE,
        page_title="Exercise Suggestion | Health & Fitness AI",
        heading="Exercise Duration & Type Recommendation",
        content=form_html + result_html
    )


# In[ ]:


@app.route("/more")
def more_section():
    import random

    # Tips and Quotes
    quotes = [
        "Push yourself, because no one else is going to do it for you.",
        "Your body can stand almost anything. It’s your mind you have to convince.",
        "Fitness is not about being better than someone else. It’s about being better than you used to be.",
        "Discipline is doing what needs to be done, even if you don’t want to do it."
    ]

    tips = [
        "Drink at least 2 liters of water daily.",
        "Warm up before workouts to prevent injury.",
        "Eat high-protein meals after strength training.",
        "Get 7–8 hours of sleep every night.",
        "Avoid skipping breakfast to maintain energy levels."
    ]

    selected_quote = random.choice(quotes)
    selected_tip = random.choice(tips)

    html = f"""
    <div class='result'>
        <h2>🧠 Fitness & Wellness Motivation</h2>
        <p style='color:#ffcc99; font-style:italic;'>{selected_quote}</p>

        <h2>📌 Tip of the Day</h2>
        <p>{selected_tip}</p>

        <h2>📅 Plan Your Day</h2>
        <p>Use our <a href="/planner" style="color:#00ccff; font-weight:bold;">Daily Health Planner</a> to build a personalized routine.</p>
    </div>
    """

    return render_template_string(
        HTML_TEMPLATE,
        page_title="More | Health & Fitness AI",
        heading="Explore More Tools & Tips",
        content=html
    )


# In[ ]:


@app.route("/planner", methods=["GET", "POST"])
def health_planner():
    plan = None

    if request.method == "POST":
        wake = request.form.get("wake_time")
        breakfast = request.form.get("breakfast_time")
        lunch = request.form.get("lunch_time")
        dinner = request.form.get("dinner_time")
        workout = request.form.get("workout_time")
        relax = request.form.get("relax_time")

        plan = {
            "Wake-up Time": wake,
            "Breakfast": breakfast,
            "Lunch": lunch,
            "Dinner": dinner,
            "Workout": workout,
            "Self-Care/Relaxation": relax
        }

    form_html = """
    <form method="POST">
        <label>Wake-up Time:</label>
        <input type="time" name="wake_time" required>

        <label>Breakfast Time:</label>
        <input type="time" name="breakfast_time" required>

        <label>Lunch Time:</label>
        <input type="time" name="lunch_time" required>

        <label>Dinner Time:</label>
        <input type="time" name="dinner_time" required>

        <label>Workout Time:</label>
        <input type="time" name="workout_time">

        <label>Relaxation Time:</label>
        <input type="time" name="relax_time">

        <button type="submit">Generate My Plan</button>
    </form>
    """

    result_html = ""
    if plan:
        result_html += "<div class='result'><h2>Your Personalized Health Plan for Today:</h2><ul>"
        for key, value in plan.items():
            result_html += f"<li><strong>{key}:</strong> {value}</li>"
        result_html += "</ul></div>"

    return render_template_string(
        HTML_TEMPLATE,
        page_title="Health Planner | Health & Fitness AI",
        heading="Daily Health & Wellness Planner",
        content=form_html + result_html
    )


# In[ ]:


if __name__ == "__main__":
    app.run(debug=False)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




