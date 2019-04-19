import lxml
from bs4 import BeautifulSoup, Tag
from openextractor.openextractor import OpenExtractor
from openextractor.recipe import Recipe
from typing import List, Union
import re


def crawl_all_recipe(bulk_insert_amt: int, clear=False) -> OpenExtractor:
    return OpenExtractor('https://www.allrecipes.com/recipe/*', 'allrecipes', bulk_insert_amt,
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
    if page.h2 is not None:
        if page.h2.text == "Ingredients":
            return True
    return False


def url_remove(url:str) -> str:
    new_url = re.sub(r'\?.*', '', url)
    return new_url


def url_check(url: str) -> bool:
    if url.find('review') == -1 and url.find('?') == -1 and url.find('/articles/') == -1 and url.find('.aspx') == -1:
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
    elements: List[Tag] = parser.select('span.recipe-ingred_txt.added')
    r_elements = []
    for ele in elements:
        if ele.text.strip() != "" and 'white' not in ele.get('class'):
            r_elements.append(ele.text.strip())
    return r_elements


def get_directions(parser: BeautifulSoup):
    elements: List[Tag] = parser.select('span.recipe-directions__list--item')
    r_elements = []
    for ele in elements:
        if ele.text.strip() != "":
            r_elements.append(ele.text.strip())
    return r_elements


def get_name(parser: BeautifulSoup) -> Union[str, None]:
    name: Tag = parser.select_one('h1')
    if name is not None:
        return name.get_text().strip()
    return None


def get_review_stats(parser):
    review_count: Tag = parser.select_one('span.review-count')
    rating: Tag= parser.select_one('div.rating-stars')
    made_it: Tag = parser.select_one('span.made-it-count')
    review_text = ""
    rating_text = ""
    made_it_text = ""

    if review_count is not None:
        review_text = review_count.get_text().strip()

    if rating is not None:
        rating_text = rating.get('data-ratingstars')

    if made_it is not None:
        if made_it.next_sibling is not None:
         made_it_text = made_it.next_sibling.text.replace(u'\xa0', u' ').strip()

    return {'review': review_text, 'rating': rating_text, 'made_it': made_it_text}


def get_nutrition_info(parser: BeautifulSoup) -> dict:
    nutrition_dict = {}
    nutri_selector: Tag= parser.select_one('div.nutrition-summary-facts')
    if nutri_selector is not None:
        nutri_elements: List[Tag] = nutri_selector.select('span')
        for ele in nutri_elements:
            nutrient_name = ele.get('itemprop')
            if nutrient_name is not None:
                nutrition_dict[nutrient_name] = ele.text.strip()
    else:
        nutri_selector: Tag = parser.select_one('div.recipe-nutrition__form')

        if nutri_selector is not None:
            nutrient_names = nutri_selector.select('li.nutrientLine__item')
            nutrient_vals = nutri_selector.select('li.nutrientLine__item--amount')

            length = len(nutrient_names)
            if len(nutrient_vals) < length:
                length = len(nutrient_vals)

            for i in range(0, length):
                try:
                    nutrition_dict[nutrient_names[i].text.strip().replace('.', '')] = nutrient_vals[i].text.strip()
                except:
                    pass

    return nutrition_dict


def get_time_info(parser: BeautifulSoup) -> List[str]:
    r_list: List[Union[str, dict]] = []
    prep_list: List[Tag] = parser.select('li.prepTime__item')
    if prep_list is not None:
        for prep in prep_list:
            prep_text =  prep.get('aria-label')
            if prep_text:
                r_list.append(prep_text)
    if len(r_list) > 0:
        return r_list
    try:
        yield_tag = parser.find(itemprop='recipeYield')
        if yield_tag is not None:
            r_list.append({'yield': yield_tag.get('content').strip()})

        ready_time = parser.select_one('span.ready-in-time')
        if ready_time is not None:
            r_list.append({'total': ready_time.text.strip()})

        prep_time = parser.find('time', itemprop='prepTime')
        if prep_time is not None:
            r_list.append({'prep': prep_time.text.strip()})

        cook_time = parser.find('time', itemprop='cookTime')
        if cook_time is not None:
            r_list.append({'cook': cook_time.text.strip()})
    except:
        return r_list

    return r_list
