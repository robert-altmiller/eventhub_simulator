# Databricks notebook source
# DBTITLE 1,Mount Storage Account
storage_account_name = "altstorageadlsgen2"
storage_account_access_key = ""
container_name = "event-hub"
mount_point = "/mnt/event-hub"

try:
  dbutils.fs.mount(
    source = f"wasbs://{container_name}@{storage_account_name}.blob.core.windows.net/",
    mount_point = mount_point,
    extra_configs = {f"fs.azure.account.key.{storage_account_name}.blob.core.windows.net": storage_account_access_key}
  )
except Exception as e:
  print(f"Error: {e}")

print(f"Container {container_name} mounted at {mount_point}")
