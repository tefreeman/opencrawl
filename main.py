from foodnetwork import crawl_food_network
from allrecipe import crawl_all_recipe
from myrecipes import crawl_my_recipes
# https://www.myrecipes.com/recipe/turkey-kefta-with-sweet-onion-raisin-sauce
# https://www.blueapron.com/recipes/vadouvan-tilapia-roasted-vegetables-with-yogurt
# www.eatingwell.com/recipes/17963/mealtimes/lunch/
# https://www.epicurious.com/recipes/food/views/steak-stroganoff
# https://www.geniuskitchen.com/recipe/chocolate-carrot-cake-roll-531031

print("0  |  foodnetwork.com crawl")
print("1  | allrecipes.com crawl")
print("2  | myrecipes.com crawl")

user_input = input("input: ")

print(user_input)
if user_input == "0":
    crawl_food_network(1, 25)
elif user_input == "1":
    crawl_all_recipe(1 , 25)
elif user_input == "2":
    crawl_my_recipes(1 , 2)


