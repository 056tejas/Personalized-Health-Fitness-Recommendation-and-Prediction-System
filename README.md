# 🧠 Personalized Health & Fitness AI Suite

A **Flask-based AI system** offering personalized health predictions and smart fitness recommendations using Machine Learning and rule-based logic. This project was developed as part of the **Upflairs 45-Day Data Science with Machine Learning & AI Internship**.

---

> ⚠️ **Note on `prediction_utils` Folder**  
> Due to GitHub’s file size and bandwidth limits, the `prediction_utils/` folder containing the trained model `.pkl` files and encoders could not be uploaded to this repository.  
>  
> To use the predictor features (Calories Burned Prediction, Macronutrient Distribution), you must first **generate the required pickle files locally** by running the notebook:  
>  
> **📄 File**: `Prediction_training.ipynb`  
>  
> This will create all necessary files inside a folder named `prediction_utils/`, including:
> - `calories_burned_model.pkl`  
> - `feature_columns.pkl`  
> - Categorical encoders (`BMI_Category_encoder.pkl`, etc.)  
> - `macros_model.pkl`  
> - `macros_feature_columns.pkl`  
>  
> After generating the files, your Flask app will run without issues.

---

## 🚀 Features

### 🔢 1. Calories Burned Prediction
- Predicts estimated calories burned during a workout.
- Inputs: **Exercise Intensity**, **Duration**, **Heart Rate**, **BMI Category**, **Fitness Level**.
- Output: Predicted calories + an **interpreted summary** (e.g., "High calorie burn – good for stamina").

---

### 🧬 2. Macronutrient Distribution Prediction
- Predicts ideal quantities of **protein**, **carbohydrates**, and **fat** based on your calorie intake.
- Inputs: **Calories**, **Meal Type**, **Diet Type**, **BMI Category**.
- Outputs:
  - Macronutrient values
  - A **donut pie chart**
  - Summary like: _"This meal is primarily composed of protein..."_

---

### 🏃‍♂️ 3. Exercise Duration & Type Recommendation
- Rule-based recommender to split available time across **Cardio, HIIT, Strength, Flexibility**.
- Inputs: **BMI Category**, **Fitness Level**, **Workout Preference**, **Fitness Goal**, **Gender**, **Time Available**.
- Output: Workout distribution bar chart + **tip of the day**.

---

### 💡 4. Smart Recommender System (Meals + Exercises)
- Suggests healthy **meal plans** and **exercise routines** tailored to:
  - BMI
  - Diet type
  - Fitness level
  - Gender
  - Time and goals
- Based on rule-based logic with fallback suggestions.
- Includes visually appealing format and user guidance.

---

### 📅 5. Daily Health Planner
- Lets users input their day’s schedule (wake, meals, workout, relaxation).
- Outputs a **personalized plan** in a clean list format.

---

### 🌟 6. More Section
- Includes:
  - Random **fitness quotes**
  - A rotating **"Tip of the Day"**
  - Quick planner access

---

## 🧠 Technologies Used

| Category      | Tools/Technologies        |
|---------------|---------------------------|
| Backend       | Flask, Python              |
| ML Models     | scikit-learn, joblib       |
| Data Handling | pandas, NumPy              |
| Visualization | Matplotlib (Pie/Bar Charts)|
| Frontend      | HTML, CSS (Flask Templates)|
| Development   | Jupyter Notebook, VS Code  |

---

## 📈 Dataset Info

- Used a combined dataset `merged_dataset.csv`.
- Included:
  - Fitness activity data
  - Calorie intake & burn
  - Macronutrient details
  - BMI, diet type, exercise info, etc.

---

## 🧪 Model Training

- Models trained using:
  - **Random Forest Regressor** for predictions
  - Encoded categorical variables using `LabelEncoder`
  - Train-test splits to validate performance

---

## Author:
Tejas Jain
