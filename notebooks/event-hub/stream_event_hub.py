# Databricks notebook source
# DBTITLE 1,Library Imports
import os, json, random, time, base64
from azure.eventhub import EventData, EventHubProducerClient

# COMMAND ----------

# DBTITLE 1,Event Hub + Storage Account Parameters
# event hub parameters
eventhub_name = "my-event-hub-2"
event_hub_connection_str = ""
event_hub_consumer_group = "$Default" 

# COMMAND ----------

# Create an EventHubProducerClient
producer_client = EventHubProducerClient.from_connection_string(event_hub_connection_str, eventhub_name=eventhub_name)

for i in range(100000000):
    try:

        num_events = 1000 # number of events to send in each batch

        # create a batch
        event_data_batch = producer_client.create_batch()

        for i in range(num_events):
            # simulated event data
            event_data = {
                "sensor_id": i,
                "temperature": random.uniform(20, 30),
                "humidity": random.uniform(40, 60),
                "timestamp": time.time()
            }
            print(event_data)

            # serialize the event data to JSON
            event_data_str = json.dumps(event_data)

            # base64 encode the JSON string
            encoded_event_data = base64.b64encode(event_data_str.encode()).decode()

            # create an EventData object with the encoded data
            event = EventData(encoded_event_data)

            try:
                # try to add the event to the batch
                event_data_batch.add(event)
            except ValueError:
                # if the batch is full, send it and create a new one
                producer_client.send_batch(event_data_batch)
                event_data_batch = producer_client.create_batch()
                event_data_batch.add(event)
            
            print(f"Queued event {i}: {encoded_event_data}")

        # send any remaining events in the final batch
        if len(event_data_batch) > 0:
            producer_client.send_batch(event_data_batch)

    except Exception as e:
        print("Exception:", e)
        producer_client.close()
        break  # Exit the loop in case of an exception

    print("Simulated events sent to Azure Event Hub.")

# close the producer client outside the loop
producer_client.close()
