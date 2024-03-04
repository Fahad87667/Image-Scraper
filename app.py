import streamlit as st
from selenium import webdriver
import os
import time
import requests
from PIL import Image
from io import BytesIO

def fetch_image_urls_bing(query: str, max_links_to_fetch: int, wd: webdriver, sleep_between_interactions: int = 1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

    search_url = f"https://www.bing.com/images/search?q={query}"
    wd.get(search_url)

    image_urls = set()
    image_count = 0
    results_start = 0

    while image_count < max_links_to_fetch:
        scroll_to_end(wd)
        thumbnail_results = wd.find_elements("css selector", "img.mimg")

        number_results = len(thumbnail_results)

        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")

        for img in thumbnail_results[results_start:number_results]:
            # Get the image source directly from the thumbnail
            src = img.get_attribute('src')
            if src and 'http' in src:
                image_urls.add(src)

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} image links, done!")
                return image_urls

        # Move the result start point further down
        results_start = len(thumbnail_results)

    print("Found:", len(image_urls), "image links, looking for more ...")
    time.sleep(30)

    return image_urls

def persist_image(folder_path: str, url: str, counter, num_columns):
    try:
        image_content = requests.get(url).content
    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        img = Image.open(BytesIO(image_content))

        # Display images in columns
        columns = st.columns(num_columns)
        column_index = counter % num_columns
        columns[column_index].image(img, caption=f"Image {counter}", use_column_width=True)
        print(f"SUCCESS - displayed {url}")
    except Exception as e:
        print(f"ERROR - Could not display {url} - {e}")

def search_and_display(search_term: str, driver_path: str, number_images=10, num_columns=3):
    st.title("Downloading Images.....")

    edge_options = webdriver.EdgeOptions()
    edge_options.use_chromium = True

    with webdriver.Edge(options=edge_options) as wd:
        res = fetch_image_urls_bing(search_term, number_images, wd=wd, sleep_between_interactions=0.5)

    if res:
        counter = 0
        for elem in res:
            persist_image(search_term, elem, counter, num_columns)
            counter += 1

        st.success("Thanks for exploring images!")
    
def main():
    st.title("ImageGalaxy Pro")

    search_term = st.text_input("Enter the search term:")
    number_images = st.slider("Number of Images to Display", 1, 50, 10)
    num_columns = st.slider("Number of Columns", 1, 5, 3)

    if st.button("Display Images"):
        search_and_display(search_term, "./msedgedriver.exe", number_images=number_images, num_columns=num_columns)

    # Add a simple footer with a link to the source code repository

if __name__ == '__main__':
    main()
