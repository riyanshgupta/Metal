def calculate_calorie_needs(weight: float, target_weight: float, height: float, age: int, gender: str, goal: str, time_frame: int, activity_level: str) -> float:
    s = 5 if gender == 'male' else -161
    bmr = 10 * weight + 6.25 * height - 5 * age + s
    if activity_level == 'sedentary':
        cal = bmr * 1.2
    elif activity_level == 'lightly active':
        cal = bmr * 1.375
    elif activity_level == 'moderately active':
        cal = bmr * 1.55
    elif activity_level == 'very active':
        cal = bmr * 1.725
    else:
        cal = bmr * 1.9
    if goal == 'maintain':
        return cal
    else:
        weight_diff = abs(target_weight - weight)
        cal_diff_per_day = weight_diff * 7700 / time_frame
        if goal == 'loose':
            return cal - cal_diff_per_day
        else:
            return cal + cal_diff_per_day
        
def macro_needs(weight: float, target_weight: float, height: float, age: int, gender: str, goal: str, time_frame: int, activity_level: str) -> dict:
    s = 5 if gender == 'male' else -161
    bmr = (10 * weight) + (6.25 * height) - (5 * age) + s
    if activity_level == 'sedentary':
        cal = bmr * 1.2
    elif activity_level == 'lightly active':
        cal = bmr * 1.375
    elif activity_level == 'moderately active':
        cal = bmr * 1.55
    elif activity_level == 'very active':
        cal = bmr * 1.725
    else:
        cal = bmr * 1.9
    if goal != 'maintain':
        weight_diff = abs(target_weight - weight)
        cal_diff_per_day = weight_diff * 7700 / time_frame
        if goal == 'loose':
            cal -= cal_diff_per_day
        else:
            cal += cal_diff_per_day
    protein = weight * 0.8
    fat = cal * 0.25 / 9
    carbs = (cal - protein * 4 - fat * 9) / 4
    carb_per = round((carbs / (carbs + fat + protein)) * 100)
    protein_per = round((protein / (carbs + fat + protein)) * 100)
    fat_per = round((fat / (carbs + fat + protein)) * 100)
    return {'protein': "{:.2f}".format(protein),
            'fat': "{:.2f}".format(fat),
            'carbs': "{:.2f}".format(carbs),
            'carb_per': carb_per,
            'protein_per': protein_per,
            'fat_per': fat_per}


