from bs4 import BeautifulSoup
import requests
import json
import os
import re

def main():
    print(len(os.listdir("data/test")))
    if len(os.listdir("data/test")) == 50:
        print(f"{len(os.listdir("data/test"))} files already downloaded.")
        return
    
    URL = "https://musescore.com/classicman/scores/105780"
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(URL, headers=headers, timeout=10)
        
        response.raise_for_status() 
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading page: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')


    scripts = soup.find_all('script')
    script = scripts[8:9]
    json_data = script[0].string.strip()
    data = json.loads(json_data)
    thumbnail_url = data.get('thumbnailUrl')
    print(thumbnail_url)
    first_link = soup.find_all('link')[0]
    svg_link = first_link.get('href')
    print(svg_link)

    if "png" in thumbnail_url:
        if "svg" in svg_link:
            svg_dl = requests.get(svg_link, stream=True, timeout=10, headers=headers, allow_redirects=True)

            name = data.get('name')
            illegal_chars_pattern = r'[<>:"/\\|?*\x00-\x1F]'
            name = re.sub(illegal_chars_pattern, "", name)
            png_dl = requests.get(thumbnail_url, stream=True, timeout=10, headers=headers, allow_redirects=True)

            # Create a directory in data/test/{name}/{name}.png
            BASE_DATA_DIR = "data"
            SUB_DIR = "test"
            score_folder_path = os.path.join(BASE_DATA_DIR, SUB_DIR, name)
            os.makedirs(score_folder_path, exist_ok=True)

            with open(f"data/test/{name}/{name}.png", 'wb') as f:
                f.write(png_dl.content)

            with open(f"data/test/{name}/{name}.svg", 'wb') as f:
                f.write(svg_dl.content)

            print(f"Downloaded {name}.png and {name}.svg")
            return None
    
    print("No PNG, SVG pair found...")


if __name__ == "__main__":
    main()
