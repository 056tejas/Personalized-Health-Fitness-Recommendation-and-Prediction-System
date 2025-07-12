#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Flask, request, render_template_string, session
import pandas as pd
import random
from recommender import recommend_meals, recommend_exercises

# Load dataset
df = pd.read_csv("merged_dataset.csv")

# Flask setup
app = Flask(__name__)
app.secret_key = 'your_secret_key'


# In[2]:


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Personalized Health & Fitness Recommendation System</title>
    <style>
        html, body {
            height: 100%;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url('https://images.unsplash.com/photo-1571019613914-85f342c41eef') no-repeat center center fixed;
            background-size: cover;
            color: #ffffff;
            overflow-x: hidden;
        }

        .container {
            background-color: rgba(0, 0, 0, 0.75);
            padding: 30px;
            border-radius: 20px;
            max-width: 800px;
            margin: 30px auto 60px auto;
            box-shadow: 0 0 20px rgba(0, 255, 204, 0.3);
        }

        h1, .app-title {
            text-align: center;
            color: #00ffcc;
            margin-bottom: 20px;
            font-size: 28px;
        }

        label {
            font-weight: bold;
            display: block;
            margin-top: 10px;
        }

        select, button {
            padding: 10px;
            width: 100%;
            margin-top: 5px;
            margin-bottom: 20px;
            border-radius: 10px;
            border: none;
            font-size: 14px;
        }

        button {
            background-color: #00cc99;
            color: white;
            cursor: pointer;
            font-weight: bold;
        }

        button:hover {
            background-color: #00b386;
        }

        .results {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }

        .tip-box {
            background-color: rgba(0, 255, 255, 0.1);
            border-left: 4px solid #00e6e6;
            padding: 15px;
            margin-top: 20px;
            margin-bottom: 30px;
            font-style: italic;
            color: #ccf2ff;
        }

        table {
            width: 100%;
            color: #fff;
            border-collapse: collapse;
            margin-top: 10px;
        }

        th, td {
            padding: 10px;
            text-align: center;
            border-bottom: 1px solid #999;
        }

        .alt-box {
            background-color: rgba(255, 255, 255, 0.08);
            padding: 15px;
            border-radius: 10px;
            margin-top: 10px;
        }

        .nav-buttons {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 20px;
        }

        .footer {
            text-align: center;
            padding: 15px 10px;
            position: fixed;
            width: 100%;
            bottom: 0;
            background: rgba(0, 0, 0, 0.85);
            font-size: 14px;
            color: #ccc;
            line-height: 1.6;
        }

        .footer a {
            color: #00e6e6;
            text-decoration: none;
            margin: 0 5px;
        }

        .footer a:hover {
            text-decoration: underline;
        }

        @media screen and (max-width: 768px) {
            .container {
                padding: 20px;
                border-radius: 15px;
            }

            select, button {
                font-size: 13px;
            }
        }
    </style>
</head>
<body>
    <div class="app-title"><h1>Personalized Health & Fitness Recommendation System</h1></div>

    <div class="container">
        {% if not hide_form %}
        <form method="post">
            <label for="goal">Fitness Goal:</label>
            <select name="goal" required>
                <option value="Loss">Loss</option>
                <option value="Gain">Gain</option>
                <option value="Maintain">Maintain</option>
            </select>

            <label for="diet_type">Diet Type:</label>
            <select name="diet_type" required>
                <option value="Balanced">Balanced</option>
                <option value="Low-Carb">Low-Carb</option>
                <option value="High-Protein">High-Protein</option>
                <option value="Vegan">Vegan</option>
            </select>

            <label for="meal_type">Meal Type:</label>
            <select name="meal_type" required>
                <option value="Breakfast">Breakfast</option>
                <option value="Lunch">Lunch</option>
                <option value="Dinner">Dinner</option>
                <option value="Snack">Snack</option>
            </select>

            <label for="fitness_level">Fitness Level:</label>
            <select name="fitness_level" required>
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
            </select>

            <label for="bmi_category">BMI Category:</label>
            <select name="bmi_category" required>
                <option value="Underweight">Underweight</option>
                <option value="Normal">Normal</option>
                <option value="Overweight">Overweight</option>
                <option value="Obese">Obese</option>
            </select>

            <button type="submit">Get Recommendations</button>
        </form>
        {% endif %}

        {% if tip_of_the_day %}
        <div class="tip-box">
            🌟 <strong>Tip of the Day:</strong> {{ tip_of_the_day }}
        </div>
        {% endif %}

        {% if show_buttons %}
        <form method="post" class="nav-buttons">
            <button type="submit" name="action" value="show_form">🔙 Back to Form</button>
            <button type="submit" name="action" value="show_history">📜 Show Last Recommendation</button>
        </form>
        {% endif %}

        {% if meals %}
        <div class="results">
            <h2>🥗 Recommended Meals</h2>
            <p>{{ meal_summary|safe }}</p>
            {{ meals|safe }}
        </div>
        {% endif %}

        {% if exercises %}
        <div class="results">
            <h2>🏋️ Recommended Exercises</h2>
            <p>{{ exercise_summary|safe }}</p>
            {{ exercises|safe }}
        </div>
        {% endif %}
    </div>

    <div class="footer">
        <div><strong>Developed by Tejas Jain</strong> | B.Tech CSE (Data Science), Poornima Institute of Engineering and Technology, Jaipur</div>
        <div>
            📧 <a href="mailto:2022pietcdtejas056@poornima.org">2022pietcdtejas056@poornima.org</a> |
            🔗 <a href="http://www.linkedin.com/in/tejas-jain-44a001261" target="_blank">LinkedIn</a> |
            💻 <a href="https://github.com/056tejas" target="_blank">GitHub</a>
        </div>
    </div>
</body>
</html>
"""


# In[3]:


TIPS = [
    "💧 Stay hydrated! Drink at least 8 glasses of water a day.",
    "🥗 Add colorful veggies to your plate — more colors = more nutrients.",
    "🏃‍♂️ Exercise for at least 30 minutes a day, 5 days a week.",
    "😴 Sleep 7–8 hours to help your body recover and grow.",
    "🍎 Balance your macronutrients: protein, fats, and carbs matter.",
    "🧘 Take a deep breath — even 5 minutes of mindfulness can help.",
    "🚶‍♂️ Walking after meals can aid digestion and stabilize blood sugar.",
    "📉 Consistency beats intensity — stick to your plan!"
]

@app.route("/", methods=["GET", "POST"])
def home():
    meals_html = ""
    exercises_html = ""
    meal_summary = ""
    exercise_summary = ""
    tip_of_the_day = random.choice(TIPS)
    hide_form = False
    show_buttons = False

    if request.method == "POST":
        action = request.form.get("action")

        if action == "show_form":
            hide_form = False
            show_buttons = False

        elif action == "show_history":
            meals_html = session.get("prev_meals", "")
            exercises_html = session.get("prev_exercises", "")
            meal_summary = session.get("prev_meal_summary", "")
            exercise_summary = session.get("prev_exercise_summary", "")
            hide_form = True
            show_buttons = True

        else:
            goal = request.form["goal"]
            diet_type = request.form["diet_type"]
            meal_type = request.form["meal_type"]
            fitness_level = request.form["fitness_level"]
            bmi_category = request.form["bmi_category"]

            meals_df = recommend_meals(df, goal, diet_type, meal_type)
            exercises_df = recommend_exercises(df, goal, fitness_level, bmi_category)

            if not meals_df.empty:
                meals_html = meals_df.to_html(index=False, classes='data', border=0)
                meal_summary = (
                    f"You are aiming for <strong>{goal.lower()}</strong> with a "
                    f"<strong>{diet_type}</strong> diet during <strong>{meal_type}</strong>. "
                    f"We’ve picked meals that support your goal by optimizing for macronutrient balance."
                )
            else:
                fallback_meals = df[df['Goal'] == goal].sort_values(by=['Protein (g)', 'Carbohydrates (g)'], ascending=[False, True]).drop_duplicates('Food_Item').head(3)
                fallback_meals = fallback_meals[['Food_Item', 'Category', 'Calories (kcal)', 'Protein (g)', 'Carbohydrates (g)', 'Fat (g)']]
                meals_html = f"""
                <div style='background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; padding: 15px; border-radius: 10px; margin-bottom: 15px;'>
                    ⚠️ <strong>No suitable meals found</strong> based on your selected goal and diet type.
                    <br>Showing 3 alternative meals instead:
                </div>
                {fallback_meals.to_html(index=False, classes='data', border=0)}
                """

            if not exercises_df.empty:
                exercises_html = exercises_df.to_html(index=False, classes='data', border=0)
                exercise_summary = (
                    f"As a <strong>{fitness_level}</strong> with a <strong>{bmi_category}</strong> BMI aiming for "
                    f"<strong>{goal.lower()}</strong>, here are tailored exercises based on your intensity level and "
                    f"calorie burn potential."
                )
            else:
                fallback_exercises = df[df['Goal'] == goal].sort_values(by='Calories Burned', ascending=False).drop_duplicates('Exercise').head(3)
                fallback_exercises = fallback_exercises[['Exercise', 'Calories Burned', 'Duration', 'Exercise Intensity', 'Heart Rate']]
                exercises_html = f"""
                <div style='background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; padding: 15px; border-radius: 10px; margin-bottom: 15px;'>
                    ⚠️ <strong>No matching exercises found</strong> for your current fitness level and BMI.
                    <br>Showing 3 alternative exercises instead:
                </div>
                {fallback_exercises.to_html(index=False, classes='data', border=0)}
                """

            # Backup current session values as previous
            session["prev_meals"] = session.get("meals", "")
            session["prev_exercises"] = session.get("exercises", "")
            session["prev_meal_summary"] = session.get("meal_summary", "")
            session["prev_exercise_summary"] = session.get("exercise_summary", "")
            
            # Store current output
            session["meals"] = meals_html
            session["exercises"] = exercises_html
            session["meal_summary"] = meal_summary
            session["exercise_summary"] = exercise_summary
            hide_form = True
            show_buttons = True

    return render_template_string(
        HTML_TEMPLATE,
        meals=meals_html,
        exercises=exercises_html,
        meal_summary=meal_summary,
        exercise_summary=exercise_summary,
        tip_of_the_day=tip_of_the_day,
        hide_form=hide_form,
        show_buttons=show_buttons
    )


# In[ ]:


if __name__ == '__main__':
    app.run(debug=False)


# In[ ]:




