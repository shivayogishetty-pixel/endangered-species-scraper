# 4_analyse.py
# This file analyses the cleaned species data from MongoDB
# I run different counts and rankings to answer business questions
# The results are saved to a separate collection called species_stats
# Student: Shivayogi Shetty | SRH University Hamburg | 2026

from config import get_database, CLEAN_COLLECTION, STATS_COLLECTION, DB_NAME
from datetime import datetime


# main function that runs all the analysis
def main():
    print("=" * 55)
    print("Data Analysis - Count and Rank")
    print("Student: Shivayogi Shetty | SRH University Hamburg")
    print("=" * 55)

    # connect to mongodb
    db, client = get_database()

    # get the clean data collection
    collection = db[CLEAN_COLLECTION]

    # check if there is data to analyse
    total = collection.count_documents({})
    print(f"\nTotal clean records to analyse: {total}")

    if total == 0:
        print("No data found. Please run 3_clean.py first.")
        client.close()
        return

    # get the stats collection to save results
    stats_collection = db[STATS_COLLECTION]
    stats_collection.drop()  # clear old results

    all_results = []

    # ---------------------------------------------------------------
    # ANALYSIS 1: COUNT species by conservation status
    # Business question: How many species are in each threat category?
    # ---------------------------------------------------------------
    print("\n--- Analysis 1: Count by Conservation Status ---")

    status_pipeline = [
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]

    status_results = list(collection.aggregate(status_pipeline))

    # add rank number to each result
    for i, item in enumerate(status_results, 1):
        item["rank"] = i
        print(f"  Rank {i}: {item['_id']} - {item['count']} species")

    # save to mongodb
    all_results.append({
        "analysis_name": "count_by_status",
        "description": "Number of species in each conservation status category",
        "results": status_results,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # ---------------------------------------------------------------
    # ANALYSIS 2: COUNT species by animal group
    # Business question: Which animal group has the most endangered species?
    # ---------------------------------------------------------------
    print("\n--- Analysis 2: Count by Animal Group ---")

    group_pipeline = [
        {"$group": {
            "_id": "$animal_group",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]

    group_results = list(collection.aggregate(group_pipeline))

    for i, item in enumerate(group_results, 1):
        item["rank"] = i
        print(f"  Rank {i}: {item['_id']} - {item['count']} species")

    all_results.append({
        "analysis_name": "count_by_animal_group",
        "description": "Number of endangered species per animal group ranked highest to lowest",
        "results": group_results,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # ---------------------------------------------------------------
    # ANALYSIS 3: COUNT and RANK the most common threats
    # Business question: What are the biggest threats to endangered species?
    # ---------------------------------------------------------------
    print("\n--- Analysis 3: Most Common Threats (Ranked) ---")

    threats_pipeline = [
        # unwind splits the threats list so each threat is its own document
        {"$unwind": "$threats_list"},
        {"$group": {
            "_id": "$threats_list",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]

    threats_results = list(collection.aggregate(threats_pipeline))

    for i, item in enumerate(threats_results, 1):
        item["rank"] = i
        print(f"  Rank {i}: {item['_id']} - {item['count']} species affected")

    all_results.append({
        "analysis_name": "top_threats_ranked",
        "description": "Top 10 most common threats to endangered species ranked by number of species affected",
        "results": threats_results,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # ---------------------------------------------------------------
    # ANALYSIS 4: COUNT species by population trend
    # Business question: Are most species populations increasing or decreasing?
    # ---------------------------------------------------------------
    print("\n--- Analysis 4: Count by Population Trend ---")

    trend_pipeline = [
        {"$match": {"population_trend": {"$ne": None}}},
        {"$group": {
            "_id": "$population_trend",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]

    trend_results = list(collection.aggregate(trend_pipeline))

    for i, item in enumerate(trend_results, 1):
        item["rank"] = i
        print(f"  Rank {i}: {item['_id']} - {item['count']} species")

    all_results.append({
        "analysis_name": "count_by_population_trend",
        "description": "Number of species for each population trend (Decreasing, Increasing, Stable)",
        "results": trend_results,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # ---------------------------------------------------------------
    # ANALYSIS 5: RANK animal orders by number of endangered species
    # Business question: Which animal orders are most at risk?
    # ---------------------------------------------------------------
    print("\n--- Analysis 5: Most Endangered Animal Orders (Ranked) ---")

    order_pipeline = [
        {"$match": {"order": {"$ne": None}}},
        {"$group": {
            "_id": "$order",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]

    order_results = list(collection.aggregate(order_pipeline))

    for i, item in enumerate(order_results, 1):
        item["rank"] = i
        print(f"  Rank {i}: {item['_id']} - {item['count']} species")

    all_results.append({
        "analysis_name": "top_endangered_orders",
        "description": "Top 10 animal orders with the most endangered species ranked",
        "results": order_results,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # ---------------------------------------------------------------
    # ANALYSIS 6: COUNT critically endangered species per animal group
    # Business question: Which group has the most critically endangered species?
    # ---------------------------------------------------------------
    print("\n--- Analysis 6: Critically Endangered Count by Group ---")

    critical_pipeline = [
        {"$match": {"status": "Critically Endangered"}},
        {"$group": {
            "_id": "$animal_group",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]

    critical_results = list(collection.aggregate(critical_pipeline))

    for i, item in enumerate(critical_results, 1):
        item["rank"] = i
        print(f"  Rank {i}: {item['_id']} - {item['count']} critically endangered species")

    all_results.append({
        "analysis_name": "critically_endangered_by_group",
        "description": "Count of critically endangered species per animal group ranked",
        "results": critical_results,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # ---------------------------------------------------------------
    # ANALYSIS 7: COUNT species with decreasing population per group
    # Business question: Which group is declining the fastest?
    # ---------------------------------------------------------------
    print("\n--- Analysis 7: Decreasing Population Count by Group ---")

    decreasing_pipeline = [
        {"$match": {"population_trend": "Decreasing"}},
        {"$group": {
            "_id": "$animal_group",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]

    decreasing_results = list(collection.aggregate(decreasing_pipeline))

    for i, item in enumerate(decreasing_results, 1):
        item["rank"] = i
        print(f"  Rank {i}: {item['_id']} - {item['count']} species with decreasing population")

    all_results.append({
        "analysis_name": "decreasing_population_by_group",
        "description": "Animal groups ranked by number of species with decreasing population",
        "results": decreasing_results,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # save all analysis results to mongodb
    print(f"\nSaving analysis results to MongoDB...")
    stats_collection.insert_many(all_results)

    print(f"Done! Saved {len(all_results)} analysis results")
    print(f"  Database   : {DB_NAME}")
    print(f"  Collection : {STATS_COLLECTION}")

    client.close()

    print(f"\nNext step: run 5_visualise.py to create charts")


if __name__ == "__main__":
    main()
