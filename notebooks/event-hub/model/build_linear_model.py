# Databricks notebook source
# DBTITLE 1,Library Imports
# library imports
import json, os, random
from datetime import datetime
from pyspark.sql.functions import rand

# machine learning imports
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator

# COMMAND ----------

# DBTITLE 1,Local Parameters
# delta lake parameters
delta_output_path = "/mnt/event-hub/event-hub-capture"

# machine learning parameters
train_test_split = .8
train_test_split_seed = 42
num_trees = 10
prediction_col = "rain_preds"
model_write_path = "/mnt/event-hub/random-forest-model"

# COMMAND ----------

# DBTITLE 1,Shared Functions
def delete_mounted_dir(dirname):
    """delete dbfs mounted directory"""
    files=dbutils.fs.ls(dirname)
    for f in files:
        if f.isDir():
            delete_mounted_dir(f.path)
        dbutils.fs.rm(f.path, recurse=True)

# COMMAND ----------

# DBTITLE 1,Read Training Dataset
df_eh_events = spark.read.load(delta_output_path, format = "delta") \
    .withColumn(prediction_col, (rand() > 0.5).cast("integer"))

# print(f"df_eh_events: {df_eh_events.count()}")
# df_eh_events.show(5, truncate = False)

# COMMAND ----------

# DBTITLE 1,Split Training Data into Train / Test Datasets
(train_df, test_df) = df_eh_events.randomSplit([train_test_split, 1- train_test_split], seed = train_test_split_seed)
test_df = test_df.drop(prediction_col)
train_row_count = train_df.count()

# print(f"train_df: {train_df.count()}")
# train_df.show(5, truncate = False)

# print(f"test_df: {test_df.count()}")
# test_df.show(5, truncate = False)

# COMMAND ----------

# DBTITLE 1,Vectorize Features, Apply Random Forest Model, Get Predictions and Upload Model
def create_upload_new_rf_model():
    """create and upload new random forest model"""

    # vectorize features (excluding 'prediction' which is the label)
    assembler = VectorAssembler(inputCols = ["sensor_id", "temperature", "humidity", "timestamp"], outputCol = "features")

    # define the random forest model
    rf = RandomForestClassifier(labelCol = prediction_col, featuresCol = "features", numTrees = num_trees)

    # define the Pipeline
    pipeline = Pipeline(stages = [assembler, rf])

    # train the Model
    model = pipeline.fit(train_df)

    # evaluate the Model
    predictions = model.transform(test_df)
    evaluator = BinaryClassificationEvaluator(labelCol = "prediction")
    accuracy = evaluator.evaluate(predictions)

    # print test accurracy
    print(f"test accuracy: {accuracy}")

    if accuracy >= .8:
        delete_mounted_dir(model_write_path)
        model.write().overwrite().save(model_write_path)
        print(f"random forest model successfully saved to: {model_write_path} because test accurracy >= .8")
    else:
        print("random forest model NOT successfully saved to: {model_write_path} because test accurracy < .8")

# COMMAND ----------

# DBTITLE 1,Create and Upload Model Tags
def create_upload_new_rf_model_tags(day_of_week, version):
    """create and upload new random forest model tags"""
    
    # create and save metadata
    metadata = {
        "model_type": "random forest",
        "model_version": version,
        "model_train_row_count": train_row_count,
        "model_tags": ['tag1', "tag2", "tag3"],
        "model_saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # save created model metadata
    metadata_path = os.path.join(f"/dbfs{model_write_path}", 'metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)
    
    print(f"tags for random forest model successfully saved to: {metadata_path}" )
