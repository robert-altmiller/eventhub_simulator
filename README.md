# eventhub_simulator
Temperature + Humidity Event Hub Simulator with Random Forest ML Model Using Pyspark Machine Learning to Predict Rain Forecast.

## Features the Event Hub Simulator Repo
- Workflow to stream events into an Azure event hub using a Databricks notebook.
- Workflow to delete Spark structured streaming event hub checkpoint folder with automation and restart read stream workflow to control how azure event hub events backlog is processed.
- Workflow to re-train Random Forest (RF) model to simulate predicting rain forecast (binary 1 or 0 prediction).  Workflow can be set to run any day of the week specified by 'day_of_week' workflow parameter.
- Workflow to read streaming events, predict rain forecast on that event hub stream in real-time, and refresh RF model in real time without workflow or cluster restart.  Workflow reloads new model into Spark driver memory while it's processing each batch of events live.
- Event hub predictions and event hub raw events are captured in Azure storage account container.  Raw events are used for retraining RF model.
- Spark machine learning RF model is stored in Azure storage account container.