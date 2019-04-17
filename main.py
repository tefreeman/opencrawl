from foodnetwork import crawl_food_network
from allrecipe import crawl_all_recipe

# https://www.myrecipes.com/recipe/turkey-kefta-with-sweet-onion-raisin-sauce
# https://www.blueapron.com/recipes/vadouvan-tilapia-roasted-vegetables-with-yogurt
# www.eatingwell.com/recipes/17963/mealtimes/lunch/
# https://www.epicurious.com/recipes/food/views/steak-stroganoff
# https://www.geniuskitchen.com/recipe/chocolate-carrot-cake-roll-531031

print("0  | for food network crawl")
print("1  | all recipe crawl")

user_input = input("input: ")

print(user_input)
if user_input == "0":
    crawl_food_network(1, 25)
elif user_input == "1":
    crawl_all_recipe(1 , 25)
