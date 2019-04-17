import lxml
from bs4 import BeautifulSoup, Tag
from openextractor.openextractor import OpenExtractor
from openextractor.recipe import Recipe
from typing import List, Union
import re


def crawl_food_network(bulk_insert_amt: int) -> OpenExtractor:
    return OpenExtractor('https://www.foodnetwork.com/recipes/*', 'foodnetwork', bulk_insert_amt,
                         extract, check, url_check, url_remove)


def extract(parser: BeautifulSoup, recipe: Recipe) -> None:

    name_ele: Tag = parser.h1

    if name_ele:
        name: str = name_ele.get_text()
        if name is not None:
            recipe.set_name(name.strip())
        else:
            recipe.append_errs("No name")
    else:
        recipe.append_errs("No name")

    # recipe Info
    keys = ['Total:', 'Level:', 'Active:', 'Prep:', 'Cook:', 'Yield:']
    recipe_info = pair_extractor(parser, keys)
    if recipe_info is not None and len(recipe_info) > 0:
        recipe.set_info(recipe_info)
    else:
        recipe.append_errs('info')

    # Ingredients
    ingredients = recursive_find_list_test(parser, 'Ingredients')
    if ingredients is not None and len(ingredients) > 0:
        recipe.set_ingredients(ingredients)
    else:
        recipe.append_errs('ingredients')

    # Directions
    directions = recursive_find_list_test(parser, 'Directions')
    if directions is not None and len(directions) > 0:
        recipe.set_directions(directions)
    else:
        recipe.append_errs('directions')


    if len(recipe.errs) > 0:
        recipe.append_parser(parser)


def recursive_find_list_test(parser: BeautifulSoup, title_search_str: str) -> List[str]:
    r_element_list: List[str] = []
    title_element: Tag = parser.find(string=title_search_str)

    if title_element is None:
        return r_element_list

    while True:
        next_element: Tag = title_element.find_next_sibling()
        if next_element is None:
            title_element = title_element.parent
        else:
            next_element1: Tag = next_element.find_next_sibling()
            if next_element1 is None:
                return build_list(next_element)
            ele_text = next_element1.text.strip()
            if len(ele_text) > 1:
                return build_list(title_element.parent)
            else:
                return build_list(next_element)


def build_list(list_parsed: BeautifulSoup, pair_mode: bool = False) -> Union[List[str], dict]:
    match_type_count: dict = {}
    match_list: list = []
    r_list: List[str] = []
    d_list: dict = {}
    new_list: List[Tag] = list_parsed.find_all(string=False)
    if len(new_list) < 1:
        return r_list

    # calculate tag rates
    for ele in new_list:
        if ele.text.strip() == '':
            new_list.remove(ele)
            continue
        ele_tag_name = ele.name
        if ele_tag_name in match_type_count:
            match_type_count[ele_tag_name] += len(re.sub(r'(\s*)(<(.*?)>)|(\s*)', '', ele.text))
        else:
            match_type_count[ele_tag_name] = len(re.sub(r'(\s*)(<(.*?)>)|(\s*)', '', ele.text))

    match_list = sort_dict_by_val(match_type_count)

    # set match tag
    if pair_mode:
        if match_list[0]['count'] != match_list[1]['count']:
            raise Exception("top two tags in match_list do not have the same count")

        tag0 = ""
        tag1 = ""
        for ele in new_list:
            if ele.name == match_list[0]['name']:
                tag0 = ele.text.strip()
            elif tag0 != "" and ele.name == match_list[1]['name']:
                tag1 = ele.text.strip()
            if tag0 != "" and tag1 != "":
                d_list[tag0] = tag1
                tag0 = ""
                tag1 = ""
        return d_list

    else:
        match_tag = match_list[0]['name']
        #choose most common tag (most likely to be list tag)
        for ele in new_list:
            if ele.name == match_tag:
                r_list.append(re.sub(r'(\s{3,})(?=[\n\t]*)', '', ele.text))

        return r_list


def key_with_max_val(d,):
    """ a) create a list of the dict's keys and values;
        b) return the key with the max value"""
    v = list(d.values())
    k = list(d.keys())
    return k[v.index(max(v))]


def pair_extractor(parser: BeautifulSoup, possible_header_strs: List[str]) -> dict:
    r_dict: dict = {}
    for key in possible_header_strs:
        val_str = parser.find(string=re.compile(r'(?i){name}'.format(name=key)))
        is_parsing: bool = True
        while is_parsing:
            if val_str is None:
                break
            sibling: Tag = val_str.find_next_sibling()
            if sibling is not None:
                text: str = sibling.text.strip()
                if text != "":
                    r_dict[key] = text
                    is_parsing = False
            val_str = val_str.parent

    return r_dict


def sort_dict_by_val(d: dict) -> List:
    match_list: list = []
    for k, v in sorted(d.items(), key=lambda kv: kv[1], reverse=True):
        match_list.append({'name': k, 'count': v})
    return match_list


def check(page: BeautifulSoup) -> bool:
    matches: int = 0
    if page is None:
        return False
    for string in page.stripped_strings:
        if string.lower().find('ingredient') != -1:
            matches += 1

    if matches > 0:
        return True
    else:
        return False


def url_remove(url:str) -> str:
    new_url = url.replace('/index.html', '').replace('.html', '')
    return re.sub(r'(-\d+)$', '', new_url)


def url_check(url: str) -> bool:
    if url.find('review') == -1 and url.find('?') == -1 and url.find('/articles/') == -1:
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
