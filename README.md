# Endangered Species Web Scraping Project

**Student:** Shivayogi Shetty  
**University:** SRH University Campus Hamburg  
**Course:** Data Management  
**Year:** Summer 2026  

---

## What is this project about?

This project scrapes data about endangered species from Wikipedia and stores it in MongoDB Atlas. The goal is to analyse which animal groups are most at risk, what the biggest threats are, and how populations are trending.

The data is scraped from Wikipedia's public endangered species list pages. Wikipedia allows scraping of its public pages so this is completely legal.

---

## Business Objective

The project answers these business questions using count and ranking:

1. How many species are in each conservation status category?
2. Which animal group has the most endangered species?
3. What are the most common threats to endangered species?
4. Are most species populations increasing or decreasing?
5. Which animal orders are most at risk?
6. Which group has the most critically endangered species?
7. Which group has the most species with decreasing population?

---

## Data Source

- **Website:** Wikipedia (en.wikipedia.org)
- **Pages scraped:** 17 list pages covering Critically Endangered, Endangered and Vulnerable species
- **Animal groups:** Mammals, Birds, Reptiles, Amphibians, Fish, Insects
- **Total species scraped:** 9,485

---

## Project Files

| File | Description |
|---|---|
| `1_scrape.py` | Main scraper - scrapes all species from Wikipedia and saves to CSV |
| `demo_scraper.py` | Demo version - scrapes only 20 species with visible browser |
| `2_csv_to_mongodb.py` | Converts CSV to JSON and uploads to MongoDB Atlas |
| `3_clean.py` | Cleans and normalizes the data in MongoDB |
| `4_analyse.py` | Runs count and rank analysis and saves results to MongoDB |
| `5_visualise.py` | Creates charts and saves them as PNG files |
| `main.py` | Runs steps 2 to 5 automatically in order |
| `config.py` | MongoDB connection settings |
| `requirements.txt` | List of Python libraries needed |
| `prompts.txt` | AI tool prompts used during development |

---

## Data Fields

Each species record has these fields:

| Field | Description | Example |
|---|---|---|
| common_name | The common name of the species | Snow Leopard |
| status | Conservation status | Critically Endangered |
| animal_group | Type of animal | Mammals |
| order | Taxonomic order | Carnivora |
| threats | Main threats to the species | habitat loss, poaching |
| population_trend | Is population going up or down | Decreasing |
| wikipedia_url | Link to the species Wikipedia page | https://en.wikipedia.org/... |
| scraped_at | When the data was scraped | 2026-05-17 10:00:00 |

---

## MongoDB Collections

The project creates 3 collections in MongoDB:

| Collection | Description | Documents |
|---|---|---|
| species_raw | Raw data directly from scraping | 9,485 |
| species_clean | Cleaned and processed data | ~9,400 |
| species_stats | Business analysis results | 7 |

---

## How to Run

### Step 1 - Clone the repository
```
https://github.com/shivayogishetty-pixel/endangered-species-scraper.git
cd endangered-species-scraper
```

### Step 2 - Create a virtual environment
```
python -m venv venv
venv\Scripts\activate
```

### Step 3 - Install required libraries
```
python -m pip install -r requirements.txt
python -m playwright install chromium
```

### Step 4 - Set up MongoDB connection
Open `config.py` and replace `YOUR_PASSWORD` with your MongoDB Atlas password:
```python
"mongodb+srv://shivayogishetty_db_user:pleTZUM9dy1L5Lo4@endangeredspecies.evn9iew.mongodb.net/?appName=EndangeredSpecies"
```

### Step 5 - Run the scraper (optional - data already in all_species.csv)
```
python 1_scrape.py
```
Screenshot of scraper running successfully done after 7 hours 
<img width="962" height="581" alt="image" src="https://github.com/user-attachments/assets/e49de6d0-2919-49d2-95d7-ec2b88f9904c" />


### Step 6 - Run the full pipeline
```
python main.py
```

This will upload the data to MongoDB, clean it, analyse it and create charts.

### Step 7 - Run the demo scraper (for presentation)
```
python demo_scraper.py
```

---

## Charts Created

The project creates 6 charts saved in the `charts/` folder:

- `chart1_status.png` - Bar chart of species by conservation status
- `chart2_animal_group.png` - Species count by animal group
- `chart3_threats.png` - Top 10 most common threats
- `chart4_population_trend.png` - Pie chart of population trends
- `chart5_orders.png` - Top 10 most endangered animal orders
- `chart6_critically_endangered.png` - Critically endangered species by group

---

## Tools and Libraries Used

| Tool | Purpose |
|---|---|
| Python 3.14 | Main programming language |
| Playwright | Opens real browser for scraping |
| BeautifulSoup4 | Reads and parses HTML |
| PyMongo | Connects to MongoDB |
| Matplotlib | Creates charts |
| MongoDB Atlas | Cloud database for storing data |
| Wikipedia | Data source for endangered species |

---

## Notes

- The scraper visits each species page individually to get threat and population trend data
- Data is auto-saved every 100 species during scraping so progress is not lost if it crashes
- The demo scraper only scrapes 20 species and takes about 3-4 minutes to run
- AI tool (Claude by Anthropic) was used for assistance during development - see prompts.txt
