# main.py
# This is the main file that runs all the steps of my project in order
# Instead of running each file one by one, I can just run this file
# and it will do everything automatically
# Student: Shivayogi Shetty | SRH University Hamburg | 2026

import time

# i import all my other scripts here so i can run them from one place
import importlib

# this function runs one step and shows a message before and after
def run_step(step_number, step_name, module_name):
    print("\n" + "=" * 55)
    print(f"STEP {step_number}: {step_name}")
    print("=" * 55)

    try:
        # import and run the module
        module = importlib.import_module(module_name)
        module.main()
        print(f"\nStep {step_number} completed successfully!")
    except Exception as e:
        print(f"\nError in step {step_number}: {e}")
        print("Please fix the error and try again.")
        return False

    # small pause between steps
    time.sleep(1)
    return True


# main function that runs all steps
def main():
    print("=" * 55)
    print("Endangered Species Data Project")
    print("Student: Shivayogi Shetty")
    print("University: SRH University Campus Hamburg")
    print("Year: 2026")
    print("=" * 55)
    print()
    print("This project scrapes endangered species data from Wikipedia")
    print("and stores it in MongoDB Atlas for analysis.")
    print()
    print("Steps:")
    print("  Step 1: Upload CSV data to MongoDB as JSON")
    print("  Step 2: Clean the data")
    print("  Step 3: Analyse the data (count and rank)")
    print("  Step 4: Create visualisation charts")
    print()
    print("Note: Make sure to run 1_scrape.py first to get the data")
    print("      and update the password in config.py before running this")
    print()

    start_time = time.time()

    # run each step one by one
    # if a step fails it stops and shows the error

    success = run_step(1, "Upload CSV to MongoDB (JSON format)", "2_csv_to_mongodb")
    if not success:
        return

    success = run_step(2, "Clean the Data", "3_clean")
    if not success:
        return

    success = run_step(3, "Analyse the Data", "4_analyse")
    if not success:
        return

    success = run_step(4, "Create Charts", "5_visualise")
    if not success:
        return

    # calculate how long it took
    end_time = time.time()
    total_time = round(end_time - start_time)
    minutes = total_time // 60
    seconds = total_time % 60

    print("\n" + "=" * 55)
    print("All steps completed successfully!")
    print(f"Total time: {minutes} minutes {seconds} seconds")
    print()
    print("Results stored in MongoDB Atlas (wwf_endangered_db):")
    print("  species_raw   - raw scraped data")
    print("  species_clean - cleaned data")
    print("  species_stats - analysis results")
    print()
    print("Charts saved in the charts/ folder:")
    print("  chart1_status.png")
    print("  chart2_animal_group.png")
    print("  chart3_threats.png")
    print("  chart4_population_trend.png")
    print("  chart5_orders.png")
    print("  chart6_critically_endangered.png")
    print("=" * 55)


if __name__ == "__main__":
    main()
