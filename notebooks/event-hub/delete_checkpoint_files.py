# Databricks notebook source
# DBTITLE 1,Remove All Files From The ADLS Gen 2 Checkpoint Folder Created and Managed by Spark
path = "/mnt/event-hub/checkpoint/"

def delete_mounted_dir(dirname):
    """delete dbfs mounted directory"""
    files=dbutils.fs.ls(dirname)
    for f in files:
        if f.isDir():
            delete_mounted_dir(f.path)
        dbutils.fs.rm(f.path, recurse=True)

delete_mounted_dir(path)
