# Databricks notebook source
# DBTITLE 1,Library Imports
from datetime import datetime

# COMMAND ----------

# DBTITLE 1,Import Notebooks
# MAGIC %run "./build_linear_model"

# COMMAND ----------

# DBTITLE 1,Create Widgets
dbutils.widgets.text("day_of_week", "thursday", "day_of_week")

# COMMAND ----------

# DBTITLE 1,Read Widgets
day_of_week = dbutils.widgets.get("day_of_week")

def get_day_of_week_number(dayofweek):
    """get day of week number"""
    dayofweek = dayofweek.lower()
    days_config = {
        "monday": 0, 
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }
    return days_config[dayofweek]

day_of_week_number = get_day_of_week_number(day_of_week)

print(f"day_of_week: {day_of_week}")
print(f"day_of_week_number: {day_of_week_number}")

# COMMAND ----------

def day_of_week(date_obj, day_of_week_number):
    # Check if the date is Thursday 
    # (weekday() returns 0 for Monday, 1 for Tuesday, ..., 6 for Sunday)
    if date_obj.weekday() == day_of_week_number: 
        return True
    else: return False

# use the current date
current_date = datetime.now()

# Check if today is a new model day
is_new_model_day = day_of_week(current_date, day_of_week_number)
print(f"today is new model day: {is_new_model_day}")
if is_new_model_day == True:
    create_upload_new_rf_model()
    create_upload_new_rf_model_tags(day_of_week, version = "1.0")
