from foodnetwork import crawl_food_network
from allrecipe import crawl_all_recipe
from myrecipes import crawl_my_recipes
from openextractor import openextractor
# https://www.myrecipes.com/recipe/turkey-kefta-with-sweet-onion-raisin-sauce
# https://www.blueapron.com/recipes/vadouvan-tilapia-roasted-vegetables-with-yogurt
# www.eatingwell.com/recipes/17963/mealtimes/lunch/
# https://www.epicurious.com/recipes/food/views/steak-stroganoff
# https://www.geniuskitchen.com/recipe/chocolate-carrot-cake-roll-531031

print("0  |  foodnetwork.com crawl")
print("1  | allrecipes.com crawl")
print("2  | myrecipes.com crawl")

user_input = input("input: ")

open_crawler: openextractor
if user_input == "0":
    open_crawler = crawl_food_network(25)
elif user_input == "1":
    open_crawler = crawl_all_recipe(25)
elif user_input == "2":
    open_crawler = crawl_my_recipes(2)
else:
    raise Exception('improper user input of, ', user_input)


print("enter subset of urls to target using this format x:x  (start:end) or enter nothing for default (all)")
user_subset = input('(x:x:): ')

if user_subset == "":
    open_crawler.run_crawl(1)
else:
    start, end = user_subset.split(',')
    open_crawler.run_crawl(int(start), int(end))



