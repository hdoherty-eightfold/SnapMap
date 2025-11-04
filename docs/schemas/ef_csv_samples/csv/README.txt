
README

Summary
The sample files provided here can be used to test the CSV ingestion functionality in Eightfold. For detailed documentation and guidelines, please refer to the following document:
https://docs.eightfold.ai/integration/csv-file-ingestion

Supported Operations with CSV Ingestion
    - Upsert: Add or update records. New data will be inserted, and existing data will be updated and combined with new entries.
    - Ingest: Add new records to the system. There are options to skip or overwrite any conflicts with existing records.
    - Update: Modify existing records. Any records that are not found will be skipped.
    - Delete: Remove specific records from the system.

Instructions for Using CSV Ingestion Sample Files
    1 The ENTITY-MAIN.csv file is mandatory for all Ingest ingestion tasks.
    2 Update the email addresses in the sample files to match your domain before proceeding with any ingestion operations.
    3 Ingestion operations will create new records in your system. Please test this thoroughly in a sandbox environment before applying it in production to avoid unintended consequences.
    4 Ensure that all the files uploaded are UTF-8 encoded.
    5 Ensure that the zip has all the files at the root and not in any folders within the zip.
    6 Ensure that there are maximum one file of each type in the zip file. For example, A zip file can contain a maximum of one main.csv file (mandatory for ingest) and one education.csv file.
