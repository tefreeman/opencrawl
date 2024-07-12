# OpenExtractor

OpenExtractor is a Python-based web scraping tool designed to extract recipe information from various cooking websites. The project uses the Beautiful Soup library for HTML parsing and Common Crawl data for fetching web page data. This project supports multiple well-known recipe websites, making it a versatile tool for gathering structured recipe information.

## Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Supported Websites](#supported-websites)
5. [File Structure](#file-structure)
6. [Contributing](#contributing)
7. [License](#license)

## Features

- **Multi-website support**: Extract recipes from multiple popular recipe websites.
- **Concurrent processing**: Uses multi-threading and multi-processing to speed up the crawling and extraction process.
- **Error handling**: Efficient error handling to skip bad URLs and handle parsing errors gracefully.
- **MongoDB Integration**: Save the extracted recipes directly into a MongoDB collection.
- **Customizable**: Easily extendable to support more websites.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/openextractor.git
    cd openextractor
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Ensure you have MongoDB installed and running on your local machine. You can download and install MongoDB [here](https://www.mongodb.com/try/download/community).

## Usage

1. To start scraping recipes, run the main script:
    ```bash
    python main.py
    ```

2. You will be prompted to choose a website to crawl. Enter the corresponding number:
    ```
    0  |  foodnetwork.com crawl
    1  |  allrecipes.com crawl
    2  |  myrecipes.com crawl
    3  |  delish.com crawl
    4  |  epicurious.com crawl
    5  |  tasteofhome.com crawl
    input: 
    ```

3. You can specify the MongoDB update rate. Press Enter to use the default (100):
    ```
    mongo update rate: 
    ```

4. Choose whether to clear previous URLs with parsing errors (Enter for no, 1 for yes):
    ```
    would you like to clear previous urls with parsing errors? (enter for no | 1 for yes): 
    ```

5. Specify a subset of URLs to target using the format `x,x` (start,end) or press Enter for default (all):
    ```
    enter subset of urls to target using this format x,x  (start,end) or enter nothing for default (all): 
    ```

## Supported Websites

- Food Network
- AllRecipes
- MyRecipes
- Delish
- Epicurious
- Taste of Home

## File Structure

- `main.py`: Entry point of the program. Handles user input and initiates the crawling process.
- `openextractor/`: Contains the main extraction logic and helper functions.
  - `openextractor.py`: Core of the OpenExtractor class handling the crawling and extraction process.
  - `recipe.py`: Definition of the Recipe class.
  - `saverecipe.py`: Logic for saving recipes to MongoDB.
  - `multiprocess.py`: Handles multi-processing logic.
- `foodnetwork.py`, `allrecipe.py`, `myrecipes.py`, `delish.py`, `epicurious.py`, `tasteofhome.py`: Contains website-specific extraction logic.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
