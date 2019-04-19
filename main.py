from foodnetwork import crawl_food_network
from allrecipe import crawl_all_recipe
from myrecipes import crawl_my_recipes
from openextractor import openextractor
from delish import crawl_delish
from epicurious import crawl_epicurious
from tasteofhome import crawl_taste_of_home

# https://www.blueapron.com/recipes/vadouvan-tilapia-roasted-vegetables-with-yogurt
# www.eatingwell.com/recipes/17963/mealtimes/lunch/
# https://www.epicurious.com/recipes/food/views/steak-stroganoff
# https://www.geniuskitchen.com/recipe/chocolate-carrot-cake-roll-531031
# Delish
print("0  |  foodnetwork.com crawl")
print("1  | allrecipes.com crawl")
print("2  | myrecipes.com crawl")
print("3  | delish.com crawl")
print("4 | epicurious.com crawl")
print("5 | tasteofhome.com crawl")

user_input = input("input: ")

update_rate = input ('mongo update rate: ')
if update_rate == "":
    update_rate = 100
else:
    update_rate = int(update_rate)
open_crawler: openextractor

if user_input == "0":
    open_crawler = crawl_food_network(update_rate)
elif user_input == "1":
    open_crawler = crawl_all_recipe(update_rate)
elif user_input == "2":
    open_crawler = crawl_my_recipes(update_rate)
elif user_input == "3":
    open_crawler = crawl_delish(update_rate)
elif user_input == "4":
    open_crawler = crawl_epicurious(update_rate)
elif user_input == "5":
    open_crawler = crawl_taste_of_home(update_rate)
else:
    raise Exception('improper user input of, ', user_input)


print("enter subset of urls to target using this format x:x  (start:end) or enter nothing for default (all)")
user_subset = input('(x:x:): ')

if user_subset == "":
    open_crawler.run_crawl(1)
else:
    start, end = user_subset.split(',')
    open_crawler.run_crawl(int(start), int(end))



