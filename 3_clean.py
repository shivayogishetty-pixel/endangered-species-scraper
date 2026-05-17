# 3_clean.py
# This file cleans the raw data that was uploaded to MongoDB
# Cleaning means fixing messy data, removing bad records,
# and making sure everything is in a consistent format
# The cleaned data is saved to a new collection called species_clean
# Student: Shivayogi Shetty | SRH University Hamburg | 2026

import re
from datetime import datetime
from config import get_database, RAW_COLLECTION, CLEAN_COLLECTION, DB_NAME


# this maps conservation status to a threat level number
# i use this later for ranking species by how endangered they are
# higher number = more endangered
THREAT_LEVEL = {
    "Critically Endangered": 3,
    "Endangered":            2,
    "Vulnerable":            1,
}


# this function fixes text by removing extra spaces and special characters
def fix_text(text):
    if not text or text == "N/A":
        return None
    # remove extra spaces
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text if text else None


# this function normalizes the conservation status
# so all values are spelled the same way
def fix_status(status):
    if not status:
        return "Unknown"
    status = status.strip()
    # make sure the status matches one of the standard values
    valid_statuses = ["Critically Endangered", "Endangered", "Vulnerable"]
    for valid in valid_statuses:
        if valid.lower() in status.lower():
            return valid
    return status


# this function takes the threats text and splits it into a list
# for example "habitat loss, poaching" becomes ["habitat loss", "poaching"]
def split_threats(threats_text):
    if not threats_text:
        return []
    # split by comma and clean each threat
    threats_list = []
    for t in threats_text.split(","):
        t = t.strip()
        if t and len(t) > 2:
            threats_list.append(t)
    return threats_list


# this function cleans one species record
def clean_one_record(record):
    # fix the common name
    common_name = fix_text(record.get("common_name"))

    # skip this record if there is no name
    if not common_name:
        return None

    # fix the conservation status
    status = fix_status(record.get("status"))

    # get the threat level number based on the status
    threat_level = THREAT_LEVEL.get(status, 0)

    # fix the animal group - make sure first letter is capital
    animal_group = fix_text(record.get("animal_group"))
    if animal_group:
        animal_group = animal_group.title()

    # fix the order name
    order = fix_text(record.get("order"))

    # split threats into a list
    threats_text = record.get("threats")
    threats_list = split_threats(threats_text) if threats_text else []

    # fix population trend
    trend = fix_text(record.get("population_trend"))
    valid_trends = ["Decreasing", "Increasing", "Stable"]
    if trend and trend not in valid_trends:
        trend = None

    # fix the wikipedia url
    url = fix_text(record.get("wikipedia_url"))

    # put together the cleaned record
    cleaned = {
        "common_name":      common_name,
        "status":           status,
        "threat_level":     threat_level,
        "animal_group":     animal_group,
        "order":            order,
        "threats":          threats_text,
        "threats_list":     threats_list,
        "population_trend": trend,
        "wikipedia_url":    url,
        "scraped_at":       record.get("scraped_at"),
        "cleaned_at":       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    return cleaned


# main function
def main():
    print("=" * 55)
    print("Data Cleaning")
    print("Student: Shivayogi Shetty | SRH University Hamburg")
    print("=" * 55)

    # connect to mongodb
    db, client = get_database()

    # get the raw data collection
    raw_collection = db[RAW_COLLECTION]

    # count how many raw records we have
    total_raw = raw_collection.count_documents({})
    print(f"\nTotal raw records in MongoDB: {total_raw}")

    if total_raw == 0:
        print("No data found. Please run 2_csv_to_mongodb.py first.")
        client.close()
        return

    # load all raw records
    print("Loading raw data...")
    raw_records = list(raw_collection.find())

    # clean each record one by one
    print("Cleaning records...")
    cleaned_records = []
    skipped = 0

    for record in raw_records:
        cleaned = clean_one_record(record)
        if cleaned:
            cleaned_records.append(cleaned)
        else:
            skipped += 1

    print(f"\nCleaning results:")
    print(f"  Total processed : {total_raw}")
    print(f"  Successfully cleaned : {len(cleaned_records)}")
    print(f"  Skipped (no name) : {skipped}")

    # remove duplicates by common name + status
    seen = set()
    unique_cleaned = []
    for record in cleaned_records:
        key = str(record.get("common_name")) + "|" + str(record.get("status"))
        if key not in seen:
            seen.add(key)
            unique_cleaned.append(record)

    duplicates = len(cleaned_records) - len(unique_cleaned)
    print(f"  Duplicates removed : {duplicates}")
    print(f"  Final clean count  : {len(unique_cleaned)}")

    # show status breakdown
    print("\nStatus breakdown after cleaning:")
    status_count = {}
    for r in unique_cleaned:
        s = r.get("status", "Unknown")
        status_count[s] = status_count.get(s, 0) + 1
    for status, count in sorted(status_count.items(), key=lambda x: -x[1]):
        print(f"  {status}: {count}")

    # show how many records have threats data
    with_threats = sum(1 for r in unique_cleaned if r.get("threats_list"))
    print(f"\nRecords with threats data: {with_threats} / {len(unique_cleaned)}")

    # show how many records have population trend data
    with_trend = sum(1 for r in unique_cleaned if r.get("population_trend"))
    print(f"Records with trend data  : {with_trend} / {len(unique_cleaned)}")

    # save cleaned data to mongodb
    print(f"\nSaving cleaned data to MongoDB...")
    clean_collection = db[CLEAN_COLLECTION]

    # delete old cleaned data first
    clean_collection.drop()

    # insert all cleaned records
    clean_collection.insert_many(unique_cleaned)

    print(f"Done! Saved {len(unique_cleaned)} clean records")
    print(f"  Database   : {DB_NAME}")
    print(f"  Collection : {CLEAN_COLLECTION}")

    client.close()

    print(f"\nNext step: run 4_analyse.py to analyse the data")


if __name__ == "__main__":
    main()
