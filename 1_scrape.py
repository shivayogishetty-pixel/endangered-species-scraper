# 1_scrape.py
# This is my main scraper file for my university project
# It scrapes endangered species data from Wikipedia
# The data is saved to a CSV file called all_species.csv
# Student: Shivayogi Shetty | SRH University Hamburg | 2026

# i looked up how to use playwright and beautifulsoup for scraping
# playwright opens a real browser so websites dont block the scraper
import csv
import time
import re
from datetime import datetime
from collections import Counter
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# the output file where all scraped data will be saved
OUTPUT_FILE = "all_species.csv"

# i set this to 9999 so it scrapes all species
# if i want to test with fewer i can change this to like 50
MAX_SPECIES = 9999

# i add a small delay between requests so wikipedia doesnt block me
DELAY_LIST   = 1.0   # delay between list pages
DELAY_DETAIL = 1.2   # delay between individual species pages

# these are all the wikipedia pages i want to scrape
# each entry has: conservation status, animal group, and the url
# i got these urls by searching wikipedia for endangered species lists
LIST_PAGES = [
    # critically endangered species pages
    ("Critically Endangered", "Mammals",    "https://en.wikipedia.org/wiki/List_of_critically_endangered_mammals"),
    ("Critically Endangered", "Birds",      "https://en.wikipedia.org/wiki/List_of_critically_endangered_birds"),
    ("Critically Endangered", "Reptiles",   "https://en.wikipedia.org/wiki/List_of_critically_endangered_reptiles"),
    ("Critically Endangered", "Amphibians", "https://en.wikipedia.org/wiki/List_of_critically_endangered_amphibians"),
    ("Critically Endangered", "Fish",       "https://en.wikipedia.org/wiki/List_of_critically_endangered_fishes"),
    ("Critically Endangered", "Insects",    "https://en.wikipedia.org/wiki/List_of_critically_endangered_insects"),
    # endangered species pages
    ("Endangered", "Mammals",    "https://en.wikipedia.org/wiki/List_of_endangered_mammals"),
    ("Endangered", "Birds",      "https://en.wikipedia.org/wiki/List_of_endangered_birds"),
    ("Endangered", "Reptiles",   "https://en.wikipedia.org/wiki/List_of_endangered_reptiles"),
    ("Endangered", "Amphibians", "https://en.wikipedia.org/wiki/List_of_endangered_amphibians"),
    ("Endangered", "Fish",       "https://en.wikipedia.org/wiki/List_of_endangered_fishes"),
    ("Endangered", "Insects",    "https://en.wikipedia.org/wiki/List_of_endangered_insects"),
    # vulnerable species pages
    ("Vulnerable", "Mammals",    "https://en.wikipedia.org/wiki/List_of_vulnerable_mammals"),
    ("Vulnerable", "Birds",      "https://en.wikipedia.org/wiki/List_of_vulnerable_birds"),
    ("Vulnerable", "Reptiles",   "https://en.wikipedia.org/wiki/List_of_vulnerable_reptiles"),
    ("Vulnerable", "Amphibians", "https://en.wikipedia.org/wiki/List_of_vulnerable_amphibians"),
    ("Vulnerable", "Fish",       "https://en.wikipedia.org/wiki/List_of_vulnerable_fishes"),
]

# these are keywords i look for when trying to find threats on a species page
THREAT_KEYWORDS = [
    "habitat loss", "deforestation", "poaching", "hunting", "climate change",
    "pollution", "overfishing", "invasive species", "disease", "drought",
    "illegal trade", "urbanization", "agriculture", "mining", "logging",
    "habitat destruction", "overexploitation", "bycatch", "wildfire",
]

# these are the column names for my csv file
CSV_FIELDS = [
    "common_name",
    "status",
    "animal_group",
    "order",
    "threats",
    "population_trend",
    "wikipedia_url",
    "scraped_at",
]


# this function loads a webpage and returns the html content
def fetch_html(url, page):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        try:
            # wait for the page title to appear
            page.wait_for_selector("h1", timeout=8000)
        except PWTimeout:
            pass
        time.sleep(0.8)
        return page.content()
    except Exception as e:
        print("    could not load page:", e)
        return None


# this function cleans up text by removing reference numbers like [1] [2]
def clean_text(text):
    if not text:
        return "N/A"
    # remove things like [1] or [edit] from wikipedia text
    text = re.sub(r"\[.*?\]", "", text)
    # remove extra spaces
    text = re.sub(r"\s+", " ", text)
    # fix special dash characters
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    return text.strip() or "N/A"


# this function saves the current list of species to the csv file
def save_to_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


# this function reads one wikipedia list page and gets all species from it
# wikipedia shows species as bullet points under headings like "Order: Carnivora"
def get_species_from_list_page(html, status, group):
    soup = BeautifulSoup(html, "html.parser")
    species_list = []

    # this keeps track of which animal order we are currently under
    current_order = "Unknown"

    # find the main content area of the wikipedia page
    content = soup.find("div", id="mw-content-text") or soup.find("div", class_="mw-parser-output")
    if not content:
        return []

    # go through each element in the page
    for tag in content.find_all(["h2", "h3", "h4", "li"]):

        # if its a heading then update the current order name
        if tag.name in ("h2", "h3", "h4"):
            heading = re.sub(r"\[.*?\]", "", tag.get_text(strip=True)).strip()
            if heading and len(heading) > 2 and "edit" not in heading.lower():
                current_order = heading

        # if its a list item then its probably a species
        elif tag.name == "li":
            text = tag.get_text(separator=" ", strip=True)

            # skip empty lines, numbered lines, and footnotes
            if not text or len(text) < 3:
                continue
            if text[0].isdigit() or text.startswith("^"):
                continue
            if len(text) > 250:
                continue

            # try to get the species common name from the link text
            common_name = "N/A"
            link = tag.find("a")
            if link:
                link_text = re.sub(r"\[.*?\]", "", link.get_text(strip=True)).strip()
                if link_text and len(link_text) > 2:
                    common_name = link_text

            # if no link then try to get name from the start of the text
            if common_name == "N/A":
                match = re.match(r"^([^(\[]+)", text)
                if match:
                    common_name = match.group(1).strip()

            # get the url to the species own wikipedia page
            species_url = "N/A"
            if link and link.get("href", "").startswith("/wiki/"):
                species_url = "https://en.wikipedia.org" + link["href"]

            # skip if we still dont have a name
            if common_name == "N/A" or len(common_name) < 3:
                continue

            # add the species to our list
            species_list.append({
                "common_name":   common_name,
                "status":        status,
                "animal_group":  group,
                "order":         current_order,
                "wikipedia_url": species_url,
            })

    return species_list


# this function visits the individual species page to get threats and population trend
def get_species_details(species, page):
    url = species.get("wikipedia_url", "N/A")

    # start with default values
    extra_info = {
        "threats":          "N/A",
        "population_trend": "N/A",
    }

    # if no url then just return the defaults
    if url == "N/A" or not url.startswith("http"):
        return {**species, **extra_info}

    html = fetch_html(url, page)
    if not html:
        return {**species, **extra_info}

    soup = BeautifulSoup(html, "html.parser")

    # wikipedia species pages have an infobox table on the right side
    # this is where i can find threats and population trend
    infobox = (
        soup.find("table", class_=re.compile(r"infobox", re.I)) or
        soup.find("table", class_=re.compile(r"biota", re.I))
    )

    if infobox:
        # go through each row of the infobox table
        for row in infobox.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if not th or not td:
                continue

            label = clean_text(th.get_text()).lower()
            value = clean_text(td.get_text(separator=", "))

            # check if this row has threat information
            if any(k in label for k in ["threat", "major threat"]):
                if extra_info["threats"] == "N/A" and value != "N/A":
                    extra_info["threats"] = value[:200]

            # check if this row has population trend information
            if any(k in label for k in ["trend", "population trend"]):
                if extra_info["population_trend"] == "N/A":
                    for t in ["Decreasing", "Increasing", "Stable", "Unknown"]:
                        if t.lower() in value.lower():
                            extra_info["population_trend"] = t
                            break
                    if extra_info["population_trend"] == "N/A" and value != "N/A":
                        extra_info["population_trend"] = value[:50]

    # if i still didnt find threats then search the whole page text
    full_text = soup.get_text().lower()

    if extra_info["threats"] == "N/A":
        found_threats = [t for t in THREAT_KEYWORDS if t in full_text]
        if found_threats:
            extra_info["threats"] = ", ".join(found_threats[:5])

    # if i still didnt find population trend then look for keywords
    if extra_info["population_trend"] == "N/A":
        if "decreasing" in full_text or "declining" in full_text:
            extra_info["population_trend"] = "Decreasing"
        elif "increasing" in full_text:
            extra_info["population_trend"] = "Increasing"
        elif "stable" in full_text:
            extra_info["population_trend"] = "Stable"

    return {**species, **extra_info}


# main function that runs the whole scraper
def main():
    print("=" * 60)
    print("Endangered Species Scraper")
    print("Student: Shivayogi Shetty | SRH University Hamburg")
    print("Source: Wikipedia (en.wikipedia.org)")
    print("Output:", OUTPUT_FILE)
    print("=" * 60)

    all_species = []

    # start the browser using playwright
    with sync_playwright() as pw:

        # headless=False means the browser window opens so we can see it
        browser = pw.chromium.launch(
            headless=False,
            args=["--no-sandbox", "--start-maximized"],
        )

        # set up the browser to look like a real user
        ctx = browser.new_context(
            viewport={"width": 1400, "height": 900},
            locale="en-US",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = ctx.new_page()

        # open wikipedia homepage first
        print("\nOpening Wikipedia...")
        page.goto("https://en.wikipedia.org", wait_until="domcontentloaded", timeout=20000)
        time.sleep(2)

        # STEP 1: go through all list pages and collect species names
        print("\n--- STEP 1: Collecting species names from Wikipedia ---")

        for i, (status, group, url) in enumerate(LIST_PAGES, 1):
            print(f"\n  [{i}/{len(LIST_PAGES)}] Getting {status} {group}...")

            html = fetch_html(url, page)
            if html:
                found = get_species_from_list_page(html, status, group)
                all_species.extend(found)
                print(f"  Found {len(found)} species. Total so far: {len(all_species)}")
            else:
                print(f"  Could not load this page, skipping...")

            time.sleep(DELAY_LIST)

        # remove duplicate species
        seen_keys = set()
        unique_species = []
        for s in all_species:
            key = s["common_name"] + "|" + s["status"]
            if key not in seen_keys:
                seen_keys.add(key)
                unique_species.append(s)

        duplicates_removed = len(all_species) - len(unique_species)
        species_to_scrape = unique_species[:MAX_SPECIES]

        print(f"\nTotal collected  : {len(all_species)}")
        print(f"Duplicates removed: {duplicates_removed}")
        print(f"Unique species   : {len(species_to_scrape)}")

        # STEP 2: visit each species page and get more details
        print(f"\n--- STEP 2: Getting details for each species ---")
        print(f"This will take a while. Auto-saves every 100 species.")
        print(f"Do NOT open the CSV file while this is running!\n")

        enriched_species = []

        for i, species in enumerate(species_to_scrape, 1):
            name = species["common_name"][:40]
            print(f"  [{i}/{len(species_to_scrape)}] {name}")

            # get extra details from the species page
            detailed = get_species_details(species, page)
            detailed["scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            enriched_species.append(detailed)

            # save every 100 species so we dont lose progress if something crashes
            if i % 100 == 0:
                save_to_csv(enriched_species, OUTPUT_FILE)
                print(f"\n  Auto-saved {i} species to {OUTPUT_FILE}\n")

            time.sleep(DELAY_DETAIL)

        print("\nClosing browser...")
        browser.close()

    # save the final data to csv
    print("\n" + "=" * 60)

    if enriched_species:
        save_to_csv(enriched_species, OUTPUT_FILE)
        print(f"Done! Scraped {len(enriched_species)} species")
        print(f"Saved to: {OUTPUT_FILE}")

        # show a quick summary of what was scraped
        print("\nSummary:")
        print("\nBy Conservation Status:")
        for status, count in Counter(s["status"] for s in enriched_species).most_common():
            print(f"  {status}: {count}")

        print("\nBy Animal Group:")
        for group, count in Counter(s["animal_group"] for s in enriched_species).most_common():
            print(f"  {group}: {count}")

        print("\nTop 5 Threats:")
        all_threats = []
        for s in enriched_species:
            if s.get("threats", "N/A") != "N/A":
                for t in s["threats"].split(","):
                    t = t.strip()
                    if t:
                        all_threats.append(t)
        for threat, count in Counter(all_threats).most_common(5):
            print(f"  {threat}: {count}")

        print(f"\nNext step: run 2_csv_to_mongodb.py to upload to MongoDB")

    else:
        print("No data was scraped. Please check your internet connection.")


# run the main function
if __name__ == "__main__":
    main()
