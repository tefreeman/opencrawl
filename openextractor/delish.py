import lxml
from bs4 import BeautifulSoup, Tag
from openextractor.openextractor import OpenExtractor
from openextractor.recipe import Recipe
from typing import List, Union
import re


def crawl_delish(bulk_insert_amt: int) -> OpenExtractor:
    return OpenExtractor('https://www.delish.com/cooking/recipe-ideas/*', 'delish', bulk_insert_amt,
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

    return


def check(page: BeautifulSoup) -> bool:
    if page is None:
        return False
    ingredient: Tag  = page.select_one('div.ingredients')
    direction: Tag = page.select_one('div.directions')
    if ingredient is not None or direction is not None:
            return True
    elif page.find(text='Ingredients') or page.find(text='Directions'):
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
    ingredient_tags: List[Tag] = parser.select('div.ingredient-item')
    if len(ingredient_tags) == 0:
        ingredient_tags = parser.select('li.recipe-ingredients-item')
    r_elements = []
    for element in ingredient_tags:
        r_text = ""
        for ele in element.stripped_strings:
            if r_text != "":
                r_text += " "
            cleaned_ele = re.sub(r'([\t\n\s])+', ' ', ele)
            if cleaned_ele != "":
              r_text += cleaned_ele
        r_elements.append(r_text)
    return r_elements


def get_directions(parser: BeautifulSoup):
    r_elements = []
    parent_element: Tag = parser.select_one('div.direction-lists')
    if parent_element is None:
        parent_element = parser.select_one('section.recipe-directions')
    if parent_element is None:
        return r_elements
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

def get_time_info(parser: BeautifulSoup) -> dict:
    r_dict: dict = {}
    prep_parent: Tag = parser.select_one('div.recipe-details-container')
    if prep_parent is None:
        prep_parent = parser.select_one('section.recipe-info')
    if prep_parent is None:
        return r_dict
    yield_ele = prep_parent.select_one('span.yields-amount')
    if yield_ele is None:
        yield_ele: Tag = prep_parent.find('div', itemprop='recipeYield')
    if yield_ele is not None:
        r_dict['yield'] =  re.sub(r'([\t\n\s])+', ' ', yield_ele.text.strip())

    prep_time_ele = prep_parent.select_one('span.prep-time-amount')
    if prep_time_ele is None:
        prep_time_ele = prep_parent.find('time', itemprop='prepTime')
    if prep_time_ele is not None:
        r_dict['prep'] =  re.sub(r'([\t\n\s])+', ' ', prep_time_ele.text.strip())

    prep_total_time = prep_parent.select_one('span.total-time-amount')
    if prep_total_time is None:
        prep_total_time = prep_parent.find('time', itemprop='totalTime')
    if prep_total_time is not None:
        r_dict['total'] =  re.sub(r'([\t\n\s])+', ' ', prep_total_time.text.strip())


    level_ele = prep_parent.select_one('div.recipe-info-item.recipe-info-difficulty')
    if level_ele is not None:
        r_dict['level'] = re.sub(r'([\t\n\s])+', ' ', level_ele.text.strip())

    return r_dict

