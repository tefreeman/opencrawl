from typing import List


class Recipe:
    # Inti
    def __init__(self, recipe=None) -> None:
        # Initialise Object with a Json array instead of using Setters.
        if recipe is not None:
            self.name = recipe.name
            self.ingredients = recipe.ingredients
            self.directions = recipe.directions
            self.review_count = recipe.review_count
            self.review_score = recipe.review_score
            self.info = recipe.info
            self.url = recipe.url
            self.errs = recipe.errs
            self.error_status = recipe.error_status
            self.parser = recipe.parser
            self.nutrition_info = recipe.nutrition_info
        else:
            self.name: str = ""
            self.ingredients: List[str] = []
            self. directions: List[str] = []
            self.review_score: int = -1
            self.review_count: int = -1
            self.info: dict = {}
            self.url: str = ""
            self.errs: List[str] = []
            self.error_status: int
            self.parser = ""
            self.nutrition_info = {}

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name \
                   and len(self.ingredients) == len(other.ingredients)\
                   and len(self.directions) == len(self.directions)\
                   and len(self.info) == len(other.info)
    # Setters and Getters
    def set_name(self, name):
        self.name = name.strip()

    def set_url(self, url):
        self.url = url

    def set_ingredients(self, ingredients):
        self.ingredients = ingredients

    def set_directions(self, directions):
        self.directions = directions

    def set_reviewCount(self, review_count):
        self.review_count = review_count

    def set_reviewScore(self, review_score):
        self.review_score = review_score

    def set_info(self, info):
        self.info = info

    def append_errs(self, err):
        self.errs.append(err)

    def get_errs(self):
        return self.errs

    def set_match_percent(self, match_percent):
        self.match_percent = match_percent

    def append_parser(self, parser):
        self.parser = parser

    def set_error_status(self, error_status):
        self.error_status = int(error_status)

    def set_nutrition_info(self, nutrition_info):
        self.nutrition_info = nutrition_info

    def FormCompleted(self):
        # TODO: Returns True if the fields have been filled in.
        if len(self.name) > 1 and len(self.ingredients) > 0 and len(self.directions) > 0 and len(self.info) > 1 and len(
                self.source_domain) > 1:
            return True
        else:
            return True

    def to_json(self):
        # Return object info via Json obj
        recipe = {
            'url': self.url,
            'name': self.name,
            'review_count': self.review_count,
            'review_score': self.review_score,
            'info': self.info,
            'directions': self.directions,
            'ingredients': self.ingredients,
            'errs': self.errs,
            'error_status': self.error_status
        }
        return recipe

    def print(self):
        print("### Printing Recipe ###")
        print(self.to_json())
        print("###        end       ###")

