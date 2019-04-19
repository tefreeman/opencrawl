import lxml
from bs4 import BeautifulSoup, Tag
from openextractor.openextractor import OpenExtractor
from openextractor.recipe import Recipe
from typing import List, Union
import re

def crawl_taste_of_home(bulk_insert_amt: int, clear=False) -> OpenExtractor:
    return OpenExtractor('https://www.tasteofhome.com/recipes/*', 'tasteofhome', bulk_insert_amt,
                         extract, check, url_check, url_remove, clear)


def extract(parser: BeautifulSoup, recipe: Recipe) -> None:

    name = get_name(parser)
    if name is None:
        recipe.append_errs('name')
    else:
        recipe.set_name(name)

    ingredients = get_ingredients(parser)
    if len(ingredients) > 0:
        recipe.set_ingredients(ingredients)
    else:
        recipe.append_errs('ingredients')

    directions = get_directions(parser)
    if len(directions) > 0:
        recipe.set_directions(directions)
    else:
        recipe.append_errs('directions')

    time_info = get_time_info(parser)
    if len(time_info) > 0:
        recipe.set_info(time_info)
    else:
        recipe.append_errs('time_info')
    '''
    description = get_description(parser)
    if description is not None:
        recipe.set_description(description)
    else:
        recipe.append_errs('description')
    '''
    '''
    nutrition = get_nutrition_info(parser)
    if len(nutrition) > 0:
        recipe.set_nutrition_info(nutrition)
    else:
        recipe.append_errs('nutrition')
    '''
    review_stats = get_review_stats(parser)
    if len(review_stats) > 0:
        if 'rating' in review_stats:
            recipe.set_reviewScore(review_stats['rating'])
        if 'review_count' in review_stats:
            recipe.set_reviewCount(review_stats['review_count'])
    else:
        recipe.append_errs('review_stats')


    return


def check(page: BeautifulSoup) -> bool:
    if page is None:
        return False
    header_tags: List[Tag]  = page.select('h2')
    for tag in header_tags:
        if tag.text.strip() == "Ingredients" or tag.text.strip() == "PREPARATION":
            return True
    if page.find(text='Ingredients') or page.find(text='Directions'):
        return True
    return False


def url_remove(url:str) -> str:
    new_url = re.sub(r'\?.*', '', url)
    return new_url


def url_check(url: str) -> bool:
    if url.find('?') == -1 and url.find('#') == -1:
        return True
    else:
        return False

def get_ingredients(parser: BeautifulSoup) -> list:
    try:
        r_elements = []
        parent_tag: Tag = parser.select_one('div.recipe-ingredients')
        if parent_tag is None:
            parent_tag = parser.select_one('ul.rd_ingredients')
        ingredient_tags: List[Tag] = parent_tag.select('li')
        for element in ingredient_tags:
            if element.text.strip() != "":
                r_elements.append(element.text.strip())
        return r_elements
    except:
        return []

def get_review_stats(parser: BeautifulSoup):
    r_dict =  {}

    parent_ele = parser.select_one('div.recipe-meta')
    if parent_ele is None:
        parent_ele = parser

    rating = 0
    rating_stars_full = parent_ele.select('i.dashicons.dashicons-star-filled')
    rating_stars_half = parent_ele.select('i.dashicons.dashicons-star-half')
    review_count = parent_ele.select_one('a.recipe-comments-scroll')

    try:
        rating += len(rating_stars_full) + (len(rating_stars_half) * 0.5)
        r_dict['rating'] = rating
    except:
        pass
    try:
        if review_count is not None:
            r_dict['review_count'] = review_count.text.strip()
    except:
        pass
    return r_dict


def get_directions(parser: BeautifulSoup):
    r_elements = []
    parent_elements: List[Tag] = parser.select('li.recipe-directions__item')
    if len(parent_elements) == 0:
        container = parser.select_one('dl.numbered-list')
        if container is not None:
            parent_elements = container.select('span.rd_name')
        else:
            parent_elements = parser.find_all(class_='rd_name')
    for parent_element in parent_elements:
        if parent_element is None:
            continue
        text = parent_element.get_text().strip()
        if text != "":
            r_elements.append(text)
    return r_elements


def get_name(parser: BeautifulSoup) -> Union[str, None]:
    name: Tag = parser.select_one('h1')
    if name is not None:
        return name.get_text().strip()
    return None

def get_description(parser: BeautifulSoup) -> str:
    parent_ele: Tag = parser.find('div', itemprop='description')
    if parent_ele is not None:
        description_ele = parent_ele.p
        if description_ele is not None:
            return description_ele.text.strip()

def get_nutrition_info(parser: BeautifulSoup) -> dict:
    nutrition_dict = {}
    nutri_selector: Tag= parser.select_one('div.nutrition.content')
    if nutri_selector is not None:
        nutri_elements: List[Tag] = nutri_selector.select('li')
        for ele in nutri_elements:
            try:
                name = ele.select_one('span.nutri-label').text.strip()
                val = ele.select_one('span.nutri-data').text.strip()
                if name is not None and val is not None:
                    nutrition_dict[name] = val
            except:
                pass
    return nutrition_dict


def get_time_info(parser: BeautifulSoup) -> dict:
    r_dict = {}
    yield_ele = parser.select_one('div.recipe-time-yield__label-servings')
    if yield_ele is None:
        yield_ele = parser.find(itemprop='recipeyield')
    if yield_ele is None:
        yield_ele = parser.select_one('span.rec-Servings')
    if yield_ele is None:
        pass
    else:
         r_dict['yield'] =  yield_ele.text.strip()

    total_time_ele = parser.select_one('div.recipe-time-yield__label-prep')
    if total_time_ele is None:
        total_time_ele = parser.find(class_='rec-CTime')
    if total_time_ele is None:
        pass
    else:
        r_dict['total'] = total_time_ele.text.strip()

    return r_dict
