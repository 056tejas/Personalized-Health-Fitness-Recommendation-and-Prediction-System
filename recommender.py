
import pandas as pd

def recommend_meals(df, goal, diet_type, meal_type):
    df_filtered = df[
        (df['Goal'] == goal) &
        (df['Diet_Type'] == diet_type) &
        (df['Meal_Type'] == meal_type) &
        (df['Calories (kcal)'] < 0.35) &
        (df['Carbohydrates (g)'] < 0.3)
    ]
    
    return df_filtered[['Food_Item', 'Category', 'Calories (kcal)', 'Protein (g)', 'Carbohydrates (g)', 'Fat (g)']].drop_duplicates().head(5)


def recommend_exercises(df, goal, fitness_level, bmi_category):
    df_filtered = df.copy()
    
    if fitness_level == 'Beginner':
        df_filtered = df_filtered[df_filtered['Exercise Intensity'] <= 4]
    elif fitness_level == 'Intermediate':
        df_filtered = df_filtered[(df_filtered['Exercise Intensity'] > 4) & (df_filtered['Exercise Intensity'] <= 7)]
    else:
        df_filtered = df_filtered[df_filtered['Exercise Intensity'] > 7]

    if goal == 'Loss':
        df_filtered = df_filtered[df_filtered['Duration'] >= 40]
    elif goal == 'Gain':
        df_filtered = df_filtered[df_filtered['Duration'] <= 40]

    if bmi_category == 'Obese':
        df_filtered = df_filtered[df_filtered['Calories Burned'] >= 300]
    elif bmi_category == 'Underweight':
        df_filtered = df_filtered[df_filtered['Calories Burned'] <= 250]
    
    return df_filtered[['Exercise', 'Calories Burned', 'Duration', 'Exercise Intensity', 'Heart Rate']].drop_duplicates().head(5)
