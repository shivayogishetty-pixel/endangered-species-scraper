# 2_csv_to_mongodb.py
# This file reads my scraped CSV file and uploads it to MongoDB Atlas
# First it converts the CSV data to JSON format
# Then it stores the JSON documents in my MongoDB cluster
# Student: Shivayogi Shetty | SRH University Hamburg | 2026

import csv
import json
from config import get_database, JSON_FILE, CSV_FILE, RAW_COLLECTION, DB_NAME


# this function reads the csv file and converts each row to a dictionary
# then it saves everything as a json file too so i can see the data format
def convert_csv_to_json(csv_path, json_path):

    print(f"Reading data from {csv_path}...")

    all_records = []

    # open and read the csv file row by row
    with open(csv_path, "r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            # convert each row into a clean json document
            # i replace N/A values with None so mongodb stores them as null
            record = {
                "common_name":      row.get("common_name")      if row.get("common_name")      != "N/A" else None,
                "status":           row.get("status")           if row.get("status")           != "N/A" else None,
                "animal_group":     row.get("animal_group")     if row.get("animal_group")     != "N/A" else None,
                "order":            row.get("order")            if row.get("order")            != "N/A" else None,
                "threats":          row.get("threats")          if row.get("threats")          != "N/A" else None,
                "population_trend": row.get("population_trend") if row.get("population_trend") != "N/A" else None,
                "wikipedia_url":    row.get("wikipedia_url")    if row.get("wikipedia_url")    != "N/A" else None,
                "scraped_at":       row.get("scraped_at")       if row.get("scraped_at")       != "N/A" else None,
            }

            all_records.append(record)

    print(f"Converted {len(all_records)} rows to JSON format")

    # save the json file so i can see what the data looks like
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(all_records, json_file, indent=2, ensure_ascii=False)

    print(f"JSON file saved to: {json_path}")

    return all_records


# this function uploads the json records to mongodb
def upload_to_mongodb(records):

    if not records:
        print("No records to upload!")
        return

    print(f"\nConnecting to MongoDB Atlas...")

    # get the database connection from config.py
    db, client = get_database()

    # get the collection where i want to store the data
    collection = db[RAW_COLLECTION]

    # delete any old data first so i dont get duplicates
    collection.drop()
    print(f"Cleared old data from {RAW_COLLECTION} collection")

    # upload in small batches so it doesnt crash
    batch_size = 500
    total_uploaded = 0

    for i in range(0, len(records), batch_size):
        # get a batch of records
        batch = records[i : i + batch_size]

        # insert the batch into mongodb
        result = collection.insert_many(batch)
        total_uploaded += len(result.inserted_ids)

        print(f"  Uploaded {total_uploaded} / {len(records)} documents...")

    # close the connection
    client.close()

    print(f"\nUpload complete!")
    print(f"  Database   : {DB_NAME}")
    print(f"  Collection : {RAW_COLLECTION}")
    print(f"  Total docs : {total_uploaded}")


# main function that runs everything
def main():
    print("=" * 55)
    print("CSV to MongoDB Uploader")
    print("Student: Shivayogi Shetty | SRH University Hamburg")
    print("=" * 55)

    # step 1: convert csv to json
    print("\n--- STEP 1: Converting CSV to JSON ---")
    records = convert_csv_to_json(CSV_FILE, JSON_FILE)

    if not records:
        print("Could not read the CSV file. Make sure all_species.csv exists.")
        return

    # show a preview of the first record
    print("\nPreview of first record in JSON format:")
    print(json.dumps(records[0], indent=2))

    # step 2: upload to mongodb
    print("\n--- STEP 2: Uploading JSON to MongoDB Atlas ---")
    upload_to_mongodb(records)

    print(f"\nNext step: run 3_clean.py to clean the data")


if __name__ == "__main__":
    main()
