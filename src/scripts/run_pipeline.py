import os
import subprocess
import sys

def ensure_data_directory():
    # Create data directory at the same level as src
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def run_spider():
    spider_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scrape", "flipkartscrape")
    output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data", "shirts.json")
    
    # Change to spider directory
    os.chdir(spider_dir)
    
    # Run the spider with output to data/shirts.json
    result = subprocess.run([
        "scrapy", "crawl", "flipscrapefull",
        "-o", output_file,
        "-t", "json"
    ])
    
    if result.returncode != 0:
        print("Error running spider")
        sys.exit(1)

def run_db_population():
    # Run the database population script
    script_path = os.path.join(os.path.dirname(__file__), "add_to_db.py")
    result = subprocess.run([sys.executable, script_path])
    
    if result.returncode != 0:
        print("Error populating database")
        sys.exit(1)

def main():
    print("Starting pipeline...")
    
    # Ensure data directory exists
    ensure_data_directory()
    
    # Run spider
    print("Running spider...")
    run_spider()
    
    # Run database population
    print("Populating database...")
    run_db_population()
    
    print("Pipeline completed successfully!")

if __name__ == "__main__":
    main()
