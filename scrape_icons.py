import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

def scrape_weapon_icons():
    """
    Scrapes weapon icons from the Endfield wiki and saves them to a local directory.
    """
    base_url = "https://endfield.wiki.gg"
    wiki_url = urljoin(base_url, "/wiki/Weapon")
    output_dir = "weapon_icons"
    
    # Retry settings
    max_retries = 3
    retry_delay = 2 # seconds

    print("Starting weapon icon scraping...")

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    try:
        # Fetch the HTML content of the page
        print(f"Fetching page: {wiki_url}")
        response = requests.get(wiki_url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse the HTML
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the container div
        navbox = soup.find("div", class_="ranger-navbox")
        if not navbox:
            print("Error: Could not find the weapon navigation box on the page.")
            return

        # Find all image tags within the navbox
        weapon_images = navbox.find_all("img")
        if not weapon_images:
            print("Error: No weapon images found in the navigation box.")
            return
            
        print(f"Found {len(weapon_images)} weapon icons. Downloading...")

        for img in weapon_images:
            if img.get("alt") and "icon.png" in img.get("alt"):
                # Get image source and alt text
                img_src = img.get("src")
                alt_text = img.get("alt")

                # Construct the full image URL
                full_img_url = urljoin(base_url, img_src)

                # Create a valid filename from the alt text
                # e.g., "Eminent Repute icon.png" -> "Eminent_Repute_icon.png"
                filename = alt_text.replace(" ", "_").replace("'", "")
                filepath = os.path.join(output_dir, filename)

                # Download the image with retry logic
                for attempt in range(max_retries):
                    try:
                        img_response = requests.get(full_img_url, stream=True)
                        img_response.raise_for_status()

                        with open(filepath, "wb") as f:
                            for chunk in img_response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                        print(f"Successfully downloaded {filename}")
                        time.sleep(1) # Delay after successful download
                        break # Exit retry loop on success

                    except requests.exceptions.RequestException as e:
                        print(f"Error downloading {full_img_url} (Attempt {attempt + 1}/{max_retries}): {e}")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay) # Delay before retrying
                        else:
                            print(f"Failed to download {filename} after {max_retries} attempts.")

        print("\nScraping complete.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the wiki page: {e}")

if __name__ == "__main__":
    scrape_weapon_icons()
