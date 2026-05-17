# config.py
# This file stores all the settings I need for my project
# I put everything here so I dont have to change it in every file
# Student: Shivayogi Shetty | SRH University Hamburg | 2026

from pymongo import MongoClient

# my mongodb atlas connection string
# replace YOUR_PASSWORD with your actual password before running
MONGO_URI = "mongodb+srv://shivayogishetty_db_user:pleTZUM9dy1L5Lo4@endangeredspecies.evn9iew.mongodb.net/?appName=EndangeredSpecies"

# name of my database in mongodb
DB_NAME = "wwf_endangered_db"

# the three collections i will be using
# species_raw = data directly from scraping
# species_clean = after cleaning the data
# species_stats = after running the analysis
RAW_COLLECTION   = "species_raw"
CLEAN_COLLECTION = "species_clean"
STATS_COLLECTION = "species_stats"

# the csv file where scraped data is saved first
CSV_FILE  = "all_species.csv"

# the json file that gets created before uploading to mongodb
JSON_FILE = "all_species.json"


# this function connects to mongodb and returns the database
# i call this function in other files to get the connection
def get_database():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db, client
