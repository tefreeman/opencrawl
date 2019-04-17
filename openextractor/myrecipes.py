import lxml
from bs4 import BeautifulSoup, Tag
from openextractor.openextractor import OpenExtractor
from openextractor.recipe import Recipe
from typing import List, Union
import re


def crawl_my_recipes(bulk_insert_amt: int) -> OpenExtractor:
    return OpenExtractor('https://www.myrecipes.com/recipe/*', 'myrecipes', bulk_insert_amt,
                         extract, check, url_check, url_remove)


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

    review_info = get_review_stats(parser)
    if len(review_info) > 0:
        recipe.set_reviewCount(review_info['review'])
        recipe.set_reviewScore(review_info['rating'])
    else:
        recipe.append_errs('review_info')

    nutrition_info = get_nutrition_info(parser)
    if len(nutrition_info) > 0:
        recipe.set_nutrition_info(nutrition_info)
    else:
        recipe.append_errs('nutrition_info')

    if len(recipe.get_errs()) > 0:
        recipe.append_parser(parser)

    return


def check(page: BeautifulSoup) -> bool:
    if page is None:
        return False
    h2_tags = page.select("h2")
    for h2 in h2_tags:
        if h2.text == "Ingredients":
            return True
    return False


def url_remove(url:str) -> str:
    new_url = re.sub(r'\?.*', '', url)
    return new_url


def url_check(url: str) -> bool:
    if url.find('?') == -1 and url.find('#') == -1 and url.find('rating') == -1\
            and url.find('review') == -1 and url.find('print') == -1:
        return True
    else:
        return False


def decompose_script_tags(parser: BeautifulSoup) -> BeautifulSoup:
    if parser:
        elements: List[Tag] = parser.find_all('script')
        if elements:
            for ele in elements:
                ele.decompose()

        nutri_tag: Tag = parser.find(text='Nutritional Analysis')
        if nutri_tag:
            par: Tag = nutri_tag.parent.parent
            par.decompose()

    return parser


def get_ingredients(parser: BeautifulSoup) -> list:
    parent_tag: Tag = parser.select_one('div.ingredients')
    ingredient_tags: List[Tag] = parent_tag.select('li')
    r_elements = []
    for ele in ingredient_tags:
        if ele.text.strip() != "":
            r_elements.append(ele.text.strip())
    return r_elements


def get_directions(parser: BeautifulSoup):
    elements: List[Tag] = parser.select('div.step')
    r_elements = []
    for element in elements:
        p_element = element.p
        if p_element is not None:
            if p_element.text.strip() != "":
                r_elements.append(p_element.text.strip())
    return r_elements


def get_name(parser: BeautifulSoup) -> Union[str, None]:
    name: Tag = parser.select_one('h1')
    if name is not None:
        return name.get_text().strip()
    return None


def get_review_stats(parser):
    review_count: Tag = parser.select_one('div.total')
    rating: Tag= parser.select_one('div.rating')

    review_count_text = ""
    rating_text = ""

    if review_count is not None:
        inner_ele = review_count.a
        if inner_ele is not None:
            review_count_text = inner_ele.get_text().strip()

    if rating is not None:
        rating_stars: List[Tag] = rating.select('span.star.on')
        rating_text = len(rating_stars)

    return {'review': review_count_text, 'rating': rating_text}


def get_nutrition_info(parser: BeautifulSoup) -> dict:
    nutrition_dict = {}
    nutri_selector: Tag= parser.select_one('div.partial.recipe-nutrition')
    if nutri_selector is not None:
        nutri_elements: List[Tag] = nutri_selector.select('li')
        for ele in nutri_elements:
            name, val = ele.text.strip().split(' ', 2)
            if name is not None and val is not None:
                nutrition_dict[name] = val
    return nutrition_dict


def get_time_info(parser: BeautifulSoup) -> dict:
    r_dict: dict = {}
    prep_parent: Tag = parser.select_one('div.recipe-meta-container')
    if prep_parent is None:
        return r_dict
    prep_list: List[Tag] = prep_parent.select('div.recipe-meta-item')
    if prep_list is None:
        return r_dict

    for prep in prep_list:
        header = prep.select_one('div.recipe-meta-item-header')
        value = prep.select_one('div.recipe-meta-item-body')
        if header is not None and value is not None:
            if header.text.strip() != "" and value.text.strip() != "":
               r_dict[header.text.strip()] = value.text.strip()
    return r_dict
