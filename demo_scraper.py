# demo_scraper.py
# This is a demo version of my scraper for presentation purposes
# It only scrapes 20 species so it runs quickly during the presentation
# The browser window opens so you can see it working live
# Student: Shivayogi Shetty | SRH University Hamburg | 2026

import csv
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# i only want 20 species for the demo
MAX_SPECIES = 20

# save the demo output to a separate file so it doesnt overwrite my main data
OUTPUT_FILE = "demo_species.csv"

# small delay between requests
DELAY = 1.2

# i will just use the critically endangered mammals page for the demo
# this is the first page i scraped in my full scraper
LIST_PAGES = [
    ("Critically Endangered", "Mammals", "https://en.wikipedia.org/wiki/List_of_critically_endangered_mammals"),
    ("Critically Endangered", "Birds",   "https://en.wikipedia.org/wiki/List_of_critically_endangered_birds"),
]

# threat keywords i search for in each species page
THREAT_KEYWORDS = [
    "habitat loss", "deforestation", "poaching", "hunting", "climate change",
    "pollution", "overfishing", "invasive species", "disease", "drought",
    "illegal trade", "urbanization", "agriculture", "mining", "logging",
    "habitat destruction", "overexploitation", "bycatch", "wildfire",
]

# columns in the output csv file
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


# this function opens a url in the browser and returns the page html
def fetch_html(url, page):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        try:
            page.wait_for_selector("h1", timeout=8000)
        except PWTimeout:
            pass
        # wait a bit so the page fully loads
        time.sleep(1.0)
        return page.content()
    except Exception as e:
        print("    Error loading page:", e)
        return None


# this removes wikipedia reference numbers like [1] [2] from text
def clean_text(text):
    if not text:
        return "N/A"
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\s+", " ", text)
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    return text.strip() or "N/A"


# this reads a wikipedia list page and gets species names from it
def get_species_from_page(html, status, group):
    soup = BeautifulSoup(html, "html.parser")
    species_list = []
    current_order = "Unknown"

    content = soup.find("div", id="mw-content-text") or soup.find("div", class_="mw-parser-output")
    if not content:
        return []

    for tag in content.find_all(["h2", "h3", "h4", "li"]):
        # update the order name when we see a heading
        if tag.name in ("h2", "h3", "h4"):
            heading = re.sub(r"\[.*?\]", "", tag.get_text(strip=True)).strip()
            if heading and len(heading) > 2 and "edit" not in heading.lower():
                current_order = heading

        # list items are the species
        elif tag.name == "li":
            text = tag.get_text(separator=" ", strip=True)
            if not text or len(text) < 3 or text[0].isdigit() or text.startswith("^"):
                continue
            if len(text) > 250:
                continue

            # get the species name from the link
            common_name = "N/A"
            link = tag.find("a")
            if link:
                link_text = re.sub(r"\[.*?\]", "", link.get_text(strip=True)).strip()
                if link_text and len(link_text) > 2:
                    common_name = link_text

            if common_name == "N/A":
                match = re.match(r"^([^(\[]+)", text)
                if match:
                    common_name = match.group(1).strip()

            # get the link to the species wikipedia page
            species_url = "N/A"
            if link and link.get("href", "").startswith("/wiki/"):
                species_url = "https://en.wikipedia.org" + link["href"]

            if common_name == "N/A" or len(common_name) < 3:
                continue

            species_list.append({
                "common_name":   common_name,
                "status":        status,
                "animal_group":  group,
                "order":         current_order,
                "wikipedia_url": species_url,
            })

    return species_list


# this visits each species page and looks for threats and population trend
def get_species_details(species, page):
    url = species.get("wikipedia_url", "N/A")

    extra_info = {
        "threats":          "N/A",
        "population_trend": "N/A",
    }

    if url == "N/A" or not url.startswith("http"):
        return {**species, **extra_info}

    html = fetch_html(url, page)
    if not html:
        return {**species, **extra_info}

    soup = BeautifulSoup(html, "html.parser")

    # look in the infobox table on the right side of the wikipedia page
    infobox = (
        soup.find("table", class_=re.compile(r"infobox", re.I)) or
        soup.find("table", class_=re.compile(r"biota", re.I))
    )

    if infobox:
        for row in infobox.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if not th or not td:
                continue
            label = clean_text(th.get_text()).lower()
            value = clean_text(td.get_text(separator=", "))

            if any(k in label for k in ["threat", "major threat"]):
                if extra_info["threats"] == "N/A" and value != "N/A":
                    extra_info["threats"] = value[:200]

            if any(k in label for k in ["trend", "population trend"]):
                if extra_info["population_trend"] == "N/A":
                    for t in ["Decreasing", "Increasing", "Stable", "Unknown"]:
                        if t.lower() in value.lower():
                            extra_info["population_trend"] = t
                            break

    # if we didnt find threats in the infobox then search the page text
    full_text = soup.get_text().lower()

    if extra_info["threats"] == "N/A":
        found_threats = [t for t in THREAT_KEYWORDS if t in full_text]
        if found_threats:
            extra_info["threats"] = ", ".join(found_threats[:5])

    # same for population trend
    if extra_info["population_trend"] == "N/A":
        if "decreasing" in full_text or "declining" in full_text:
            extra_info["population_trend"] = "Decreasing"
        elif "increasing" in full_text:
            extra_info["population_trend"] = "Increasing"
        elif "stable" in full_text:
            extra_info["population_trend"] = "Stable"

    return {**species, **extra_info}


# main function
def main():
    print("=" * 55)
    print("DEMO SCRAPER - Endangered Species Project")
    print("Student: Shivayogi Shetty | SRH University Hamburg")
    print(f"Scraping {MAX_SPECIES} species for demonstration")
    print("=" * 55)

    all_species = []

    with sync_playwright() as pw:

        # headless=False so the browser opens and professor can see it
        browser = pw.chromium.launch(
            headless=False,
            args=["--no-sandbox", "--start-maximized"],
        )

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

        # open wikipedia first
        print("\nOpening Wikipedia in browser...")
        print("(you can watch the browser scrape the data live!)")
        page.goto("https://en.wikipedia.org", wait_until="domcontentloaded", timeout=20000)
        time.sleep(2)

        # STEP 1: get species names from the list pages
        print("\n--- STEP 1: Getting species names ---")

        for status, group, url in LIST_PAGES:
            print(f"\nLoading: {url}")
            html = fetch_html(url, page)
            if html:
                found = get_species_from_page(html, status, group)
                all_species.extend(found)
                print(f"Found {len(found)} {group} species")
            time.sleep(1.0)

            # stop collecting once we have enough for the demo
            if len(all_species) >= MAX_SPECIES * 2:
                break

        # remove duplicates and take only 20
        seen = set()
        unique = []
        for s in all_species:
            key = s["common_name"] + "|" + s["status"]
            if key not in seen:
                seen.add(key)
                unique.append(s)

        demo_species = unique[:MAX_SPECIES]
        print(f"\nSelected {len(demo_species)} species for demo")

        # STEP 2: visit each species page to get details
        print(f"\n--- STEP 2: Getting details for each species ---")

        results = []
        for i, species in enumerate(demo_species, 1):
            print(f"  [{i}/{len(demo_species)}] Scraping: {species['common_name']}")
            detailed = get_species_details(species, page)
            detailed["scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            results.append(detailed)
            time.sleep(DELAY)

        print("\nClosing browser...")
        browser.close()

    # save results to csv
    print("\n" + "=" * 55)

    if results:
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(results)

        print(f"Done! Scraped {len(results)} species")
        print(f"Saved to: {OUTPUT_FILE}")

        # show results in terminal
        print("\nSpecies scraped:")
        print("-" * 40)
        for s in results:
            print(f"  {s['common_name']} ({s['status']})")

        print(f"\nThis is a demo of my full scraper which scraped 9000+ species")
        print(f"Full data is stored in MongoDB Atlas (wwf_endangered_db)")
    else:
        print("No data scraped. Check internet connection.")


if __name__ == "__main__":
    main()
