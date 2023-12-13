# Databricks notebook source
# DBTITLE 1,Library Imports
# library imports
import json, os, time
from pyspark.sql.functions import col, expr, from_json
from pyspark.sql.utils import StreamingQueryException
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType

# machine learning imports
from pyspark.ml import PipelineModel

# COMMAND ----------

# DBTITLE 1,Setup Databricks Widgets
dbutils.widgets.text("mins_to_simulated_failure", "100", "mins_to_simulated_failure")

# COMMAND ----------

# DBTITLE 1,Local Parameters
# event hub parameters
eventhub_name = "my-event-hub-2"
event_hub_connection_str = ""
event_hub_consumer_group = "$Default"

# delta lake parameters
delta_output_path = "/mnt/event-hub/event-hub-capture"
delta_preds_output_path = "/mnt/event-hub/event-hub-capture-predictions"

# general program execution parameters
mins_to_simulated_failure = int(dbutils.widgets.get("mins_to_simulated_failure"))
print(f"mins_to_simulated_failure: {mins_to_simulated_failure}")

# machine learning parameters
model_path = "/mnt/event-hub/random-forest-model"
model_metadata_path = os.path.join(f"/dbfs{model_path}", 'metadata.json')

# COMMAND ----------

# DBTITLE 1,Read Event Hub Events Using Spark
# define the Event Hub configuration
ehConf = {}

ehConf['eventhubs.connectionString'] = sc._jvm.org.apache.spark.eventhubs.EventHubsUtils.encrypt(f"{event_hub_connection_str};EntityPath={eventhub_name}")

# read from the Event Hub
df = spark.readStream.format("eventhubs") \
    .options(**ehConf) \
    .load()

# safely decode the base64 encoded data in the 'body' column
decoded_df = df.withColumn("decoded_body", expr("decode(unbase64(body), 'UTF-8')"))

# track the start time
start_time = time.time()

# define a function to process each micro-batch
def process_batch(batch_df, batch_id):

    # structure and show a sample of the data
    schema = StructType([
        StructField("sensor_id", IntegerType(), True),
        StructField("temperature", DoubleType(), True),
        StructField("humidity", DoubleType(), True),
        StructField("timestamp", DoubleType(), True)
    ])
    batch_df_parsed = batch_df.withColumn("parsed", from_json(col("decoded_body"), schema))
    batch_df_final = batch_df_parsed.select(col("parsed.sensor_id"), col("parsed.temperature"), col("parsed.humidity"), col("parsed.timestamp"))
    batch_df_final.show(5, truncate = False)


    # write event hub data dataFrame to delta lake
    batch_df_final.write.format("delta").mode("append").save(delta_output_path)
    #spark.sql(f"OPTIMIZE '{delta_output_path}'")
    spark.sql(f"VACUUM '{delta_output_path}'")


    # load random forest model and metadata and get predictions on streaming data
    rf_model = PipelineModel.load(model_path) # !!! uploads model to memory on each batch !!!
    with open(model_metadata_path, 'r') as f:
        metadata = json.load(f)
    print(f"rf_model_metadata: {metadata}")  # prints the loaded metadata
    batch_df_final_preds = rf_model.transform(batch_df_final)


    # write event hub predictions data to delta lake
    batch_df_final_preds.show(5, truncate = False)
    batch_df_final_preds.write.format("delta").mode("append").save(delta_preds_output_path)
    #spark.sql(f"OPTIMIZE '{delta_preds_output_path}'")
    spark.sql(f"VACUUM '{delta_preds_output_path}'")


    # calculate elapsed time in minutes
    elapsed_time_minutes = (time.time() - start_time) / 60
    print(f"elapsed_time_minutes: {elapsed_time_minutes}")


    # check if elapsed time is greater than 'mins_to_simulated_failure'
    if elapsed_time_minutes > mins_to_simulated_failure:
        raise StreamingQueryException(f"simulated error after {mins_to_simulated_failure} minutes...")


# define the checkpoint location
checkpointLocation = "/mnt/event-hub/checkpoint"

# process the decoded stream and write it with checkpointing using foreachBatch
query = decoded_df.writeStream \
    .outputMode("append") \
    .foreachBatch(process_batch) \
    .option("checkpointLocation", checkpointLocation) \
    .start()

query.awaitTermination()
