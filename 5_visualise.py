# 5_visualise.py
# This file creates charts and graphs from my analysis results
# I use matplotlib to make bar charts and pie charts
# The charts are saved as PNG image files
# Student: Shivayogi Shetty | SRH University Hamburg | 2026

import matplotlib.pyplot as plt
import os
from config import get_database, STATS_COLLECTION

# folder where i will save all the chart images
CHARTS_FOLDER = "charts"


# this creates the charts folder if it doesnt exist already
def create_charts_folder():
    if not os.path.exists(CHARTS_FOLDER):
        os.makedirs(CHARTS_FOLDER)
        print(f"Created folder: {CHARTS_FOLDER}")


# this gets one analysis result from mongodb by its name
def get_analysis(stats_collection, analysis_name):
    result = stats_collection.find_one({"analysis_name": analysis_name})
    if not result:
        print(f"  Could not find analysis: {analysis_name}")
        return None
    return result["results"]


# CHART 1: bar chart showing species count by conservation status
def chart_status(stats_collection):
    print("  Creating chart 1: Species by Conservation Status...")

    data = get_analysis(stats_collection, "count_by_status")
    if not data:
        return

    # get labels and values from the data
    labels = [item["_id"] for item in data]
    values = [item["count"] for item in data]

    # create the bar chart
    fig, ax = plt.subplots(figsize=(8, 5))

    # use different colors for each status
    colors = ["#d32f2f", "#f57c00", "#fbc02d"]
    bars = ax.bar(labels, values, color=colors[:len(labels)], edgecolor="black", width=0.5)

    # add the count number on top of each bar
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 10,
            str(value),
            ha="center",
            fontsize=11,
            fontweight="bold"
        )

    # add titles and labels
    ax.set_title("Number of Species by Conservation Status", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Conservation Status", fontsize=11)
    ax.set_ylabel("Number of Species", fontsize=11)
    ax.set_ylim(0, max(values) + 200)

    plt.tight_layout()
    path = os.path.join(CHARTS_FOLDER, "chart1_status.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


# CHART 2: horizontal bar chart showing species count by animal group
def chart_animal_group(stats_collection):
    print("  Creating chart 2: Species by Animal Group...")

    data = get_analysis(stats_collection, "count_by_animal_group")
    if not data:
        return

    labels = [item["_id"] for item in data]
    values = [item["count"] for item in data]

    # i use a horizontal bar chart because the group names are long
    fig, ax = plt.subplots(figsize=(9, 5))

    colors = ["#1565c0", "#283593", "#4527a0", "#6a1b9a", "#880e4f", "#b71c1c"]
    bars = ax.barh(labels, values, color=colors[:len(labels)], edgecolor="black")

    # add count labels at the end of each bar
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_width() + 10,
            bar.get_y() + bar.get_height() / 2,
            str(value),
            va="center",
            fontsize=10,
            fontweight="bold"
        )

    ax.set_title("Number of Endangered Species by Animal Group", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Number of Species", fontsize=11)
    ax.set_ylabel("Animal Group", fontsize=11)
    ax.set_xlim(0, max(values) + 150)

    plt.tight_layout()
    path = os.path.join(CHARTS_FOLDER, "chart2_animal_group.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


# CHART 3: horizontal bar chart for top 10 threats
def chart_threats(stats_collection):
    print("  Creating chart 3: Top 10 Threats...")

    data = get_analysis(stats_collection, "top_threats_ranked")
    if not data:
        return

    # reverse the list so highest is at the top
    labels = [item["_id"] for item in reversed(data)]
    values = [item["count"] for item in reversed(data)]

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.barh(labels, values, color="#c62828", edgecolor="black")

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_width() + 5,
            bar.get_y() + bar.get_height() / 2,
            str(value),
            va="center",
            fontsize=9,
            fontweight="bold"
        )

    ax.set_title("Top 10 Most Common Threats to Endangered Species", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Number of Species Affected", fontsize=11)
    ax.set_ylabel("Threat Type", fontsize=11)
    ax.set_xlim(0, max(values) + 150)

    plt.tight_layout()
    path = os.path.join(CHARTS_FOLDER, "chart3_threats.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


# CHART 4: pie chart for population trend
def chart_population_trend(stats_collection):
    print("  Creating chart 4: Population Trend...")

    data = get_analysis(stats_collection, "count_by_population_trend")
    if not data:
        return

    labels = [item["_id"] for item in data]
    values = [item["count"] for item in data]

    # colors for each trend type
    colors = ["#e53935", "#43a047", "#1e88e5"]

    fig, ax = plt.subplots(figsize=(7, 6))

    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colors[:len(labels)],
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops={"linewidth": 2, "edgecolor": "white"}
    )

    # make the percentage text bigger
    for autotext in autotexts:
        autotext.set_fontsize(11)
        autotext.set_fontweight("bold")

    ax.set_title("Population Trend of Endangered Species", fontsize=14, fontweight="bold", pad=15)

    plt.tight_layout()
    path = os.path.join(CHARTS_FOLDER, "chart4_population_trend.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


# CHART 5: bar chart for top 10 most endangered animal orders
def chart_orders(stats_collection):
    print("  Creating chart 5: Top 10 Endangered Animal Orders...")

    data = get_analysis(stats_collection, "top_endangered_orders")
    if not data:
        return

    labels = [item["_id"] for item in reversed(data)]
    values = [item["count"] for item in reversed(data)]

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.barh(labels, values, color="#2e7d32", edgecolor="black")

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_width() + 2,
            bar.get_y() + bar.get_height() / 2,
            str(value),
            va="center",
            fontsize=9,
            fontweight="bold"
        )

    ax.set_title("Top 10 Animal Orders with Most Endangered Species", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Number of Species", fontsize=11)
    ax.set_ylabel("Animal Order", fontsize=11)
    ax.set_xlim(0, max(values) + 50)

    plt.tight_layout()
    path = os.path.join(CHARTS_FOLDER, "chart5_orders.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


# CHART 6: bar chart for critically endangered species per group
def chart_critically_endangered(stats_collection):
    print("  Creating chart 6: Critically Endangered by Group...")

    data = get_analysis(stats_collection, "critically_endangered_by_group")
    if not data:
        return

    labels = [item["_id"] for item in data]
    values = [item["count"] for item in data]

    fig, ax = plt.subplots(figsize=(9, 5))

    bars = ax.bar(labels, values, color="#b71c1c", edgecolor="black", width=0.5)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 2,
            str(value),
            ha="center",
            fontsize=10,
            fontweight="bold"
        )

    ax.set_title("Critically Endangered Species Count by Animal Group", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Animal Group", fontsize=11)
    ax.set_ylabel("Number of Species", fontsize=11)
    ax.set_ylim(0, max(values) + 80)

    plt.tight_layout()
    path = os.path.join(CHARTS_FOLDER, "chart6_critically_endangered.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


# main function that runs all the charts
def main():
    print("=" * 55)
    print("Data Visualisation - Creating Charts")
    print("Student: Shivayogi Shetty | SRH University Hamburg")
    print("=" * 55)

    # create the charts folder
    create_charts_folder()

    # connect to mongodb
    db, client = get_database()
    stats_collection = db[STATS_COLLECTION]

    # check if there is analysis data
    total = stats_collection.count_documents({})
    if total == 0:
        print("No analysis data found. Please run 4_analyse.py first.")
        client.close()
        return

    print(f"\nCreating charts from {total} analysis results...")
    print()

    # create all 6 charts
    chart_status(stats_collection)
    chart_animal_group(stats_collection)
    chart_threats(stats_collection)
    chart_population_trend(stats_collection)
    chart_orders(stats_collection)
    chart_critically_endangered(stats_collection)

    client.close()

    print(f"\nAll charts saved to: {CHARTS_FOLDER}/")
    print("\nCharts created:")
    print("  chart1_status.png              - species by conservation status")
    print("  chart2_animal_group.png        - species by animal group")
    print("  chart3_threats.png             - top 10 threats")
    print("  chart4_population_trend.png    - population trend pie chart")
    print("  chart5_orders.png              - top 10 endangered orders")
    print("  chart6_critically_endangered.png - critically endangered by group")
    print("\nProject complete!")


if __name__ == "__main__":
    main()
