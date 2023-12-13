# Databricks notebook source
# DBTITLE 1,Read Prediction Results
preds_path = "/mnt/event-hub/event-hub-capture-predictions"
streaming_preds_df = spark.read.load(preds_path)
print(f"total rows: {streaming_preds_df.count()}")
streaming_preds_df.show(100, truncate = False)

# COMMAND ----------


