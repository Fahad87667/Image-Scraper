from flask import Flask, render_template, request
from selenium import webdriver
import os
import time
import requests

app = Flask(__name__)

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

def persist_image(folder_path: str, url: str, counter):
    try:
        image_content = requests.get(url).content
    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        f = open(os.path.join(folder_path, f"img_{counter}.jpg"), 'wb')
        f.write(image_content)
        f.close()
        print(f"SUCCESS - saved {url} - as {folder_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")

def search_and_download(search_term: str, driver_path: str, number_images=10):
    target_folder = os.path.join('./images', '_'.join(search_term.lower().split(' ')))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    edge_options = webdriver.EdgeOptions()
    edge_options.use_chromium = True

    with webdriver.Edge(options=edge_options, executable_path=driver_path) as wd:
        res = fetch_image_urls_bing(search_term, number_images, wd=wd, sleep_between_interactions=0.5)

    if res:
        counter = 0
        for elem in res:
            persist_image(target_folder, elem, counter)
            counter += 1

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_term = request.form['search_term']
        driver_path = request.form['driver_path']
        number_images = int(request.form['number_images'])

        search_and_download(search_term, driver_path, number_images=number_images)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False)