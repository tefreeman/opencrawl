import lxml
from bs4 import BeautifulSoup, Tag
from openextractor.openextractor import OpenExtractor
from openextractor.recipe import Recipe
from typing import List, Union
import re


def crawl_epicurious(bulk_insert_amt: int, clear=False) -> OpenExtractor:
    return OpenExtractor('https://www.epicurious.com/recipes/food/views/*', 'epicurious', bulk_insert_amt,
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

    description = get_description(parser)
    if description is not None:
        recipe.set_description(description)
    else:
        pass

    nutrition = get_nutrition_info(parser)
    if len(nutrition) > 0:
        recipe.set_nutrition_info(nutrition)
    else:
       pass

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
    ingredient_tags: List[Tag] = parser.select('li.ingredient')
    if len(ingredient_tags) == 0:
       ingredient_tags = parser.find_all(itemprop='ingredients')
    r_elements = []
    for element in ingredient_tags:
        if element.text.strip() != "":
            r_elements.append(element.text.strip())
    return r_elements

def get_review_stats(parser: BeautifulSoup):
    r_dict =  {}

    parent_ele = parser.select_one('recipe-sidebar')
    if parent_ele is None:
        parent_ele = parser

    rating = parent_ele.find(itemprop='ratingValue')
    review_count = parent_ele.find(itemprop='reviewCount')

    try:
        if rating is not None:
            r_dict['rating'] = rating['content'].strip()
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
    parent_elements: List[Tag] = parser.select('ol.preparation-steps')
   # if parent_element is None:
   #     parent_element = parser.select_one('section.recipe-directions')
    if len(parent_elements) == 0:
        return r_elements
    for parent_element in parent_elements:
        if parent_element is None:
            continue
        elements = parent_element.select('li')
        for element in elements:
            if element.text.strip() != "":
                r_elements.append(element.text.strip())
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
                    nutrition_dict[name.replace('.', '')] = val
            except:
                pass
    return nutrition_dict


def get_time_info(parser: BeautifulSoup) -> dict:
    r_dict = {}
    yield_ele = parser.find(itemprop='recipeYield')
    if yield_ele is None:
        pass
    else:
         r_dict['yield'] =  yield_ele.text.strip()

    total_time_ele = parser.select_one('dd.total-time')
    if total_time_ele is None:
        pass
    else:
        r_dict['total'] = total_time_ele.text.strip()

    active_time_ele = parser.select_one('dd.active-time')
    if active_time_ele is None:
        pass
    else:
        r_dict['active'] = active_time_ele.text.strip()

    return r_dict