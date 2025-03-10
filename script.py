import streamlit as st
import json
import os
from PIL import Image
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the ADMIN_PASSWORD from environment variables
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


# Define paths
RECIPE_FILE = "recipes.json"
IMAGE_DIR = "recipe_images"
Path(IMAGE_DIR).mkdir(parents=True, exist_ok=True)

# Load recipes function
def load_recipes():
    if "recipes" not in st.session_state:
        if os.path.exists(RECIPE_FILE):
            try:
                with open(RECIPE_FILE, "r") as f:
                    st.session_state.recipes = json.load(f)
            except json.JSONDecodeError:
                st.warning("Corrupted recipe file. Starting fresh.")
                st.session_state.recipes = {}
        else:
            st.session_state.recipes = {}

# Save recipes function
def save_recipes():
    with open(RECIPE_FILE, "w") as f:
        json.dump(st.session_state.recipes, f, indent=4)

load_recipes()

# Admin password input and validation
admin_password = st.text_input("Admin Password", type="password")

# Check if entered password matches the ADMIN_PASSWORD
if admin_password == ADMIN_PASSWORD:
    st.session_state.is_admin = True
    st.success("Logged in as Admin!")
else:
    st.session_state.is_admin = False
    if admin_password:
        st.error("Incorrect password! Please try again.")

st.sidebar.header("Recipe Categories")
selected_category = st.sidebar.selectbox("Choose a category", ["Select a category"] + list(st.session_state.recipes.keys()))

# Button to show Add Recipe form
if st.sidebar.button("Add New Recipe"):
    st.session_state.show_add_recipe = True

# Main title and introduction
st.title("Flavor Fusion")
st.markdown("### Discover, Cook & Savor with Flavor Fusion!")

# Recipe search functionality
search_query = st.text_input("Search for a recipe")
search_results = []

if search_query:
    for category, recipes in st.session_state.recipes.items():
        for recipe in recipes:
            if search_query.lower() in recipe["title"].lower():
                search_results.append((category, recipe))

# Display search results
if search_query and search_results:
    st.subheader("Search Results")
    for category, recipe in search_results:
        with st.container():
            st.subheader(recipe["title"])
            col1, col2 = st.columns([1, 2])
            if recipe.get("image") and os.path.exists(recipe["image"]):
                col1.image(recipe["image"], caption=recipe["title"], use_container_width=True)
            with col2:
                st.markdown(f"**Category:** {category}")
                st.markdown(f"**Cooking Time:** {recipe['cooking_time']}")
                st.markdown(f"**Added by:** {recipe.get('user', 'Unknown')}")
                with st.expander("Ingredients"):
                    st.write("\n".join([f"- {ing}" for ing in recipe["ingredients"]]))
                with st.expander("Instructions"):
                    st.write(recipe["instructions"])
            if st.session_state.is_admin:
                if st.button(f"Delete {recipe['title']}", key=f"delete_{recipe['title']}"):
                    st.session_state.recipes[category].remove(recipe)
                    save_recipes()
                    st.success(f"Recipe '{recipe['title']}' deleted successfully!")
                    st.experimental_rerun()
            st.markdown("---")

elif search_query:
    st.warning("No recipe found! You can add a new recipe below.")
    st.session_state.show_add_recipe = True

# Display recipes from the selected category
if selected_category != "Select a category" and not search_query:
    st.subheader(f"{selected_category}")
    for recipe in st.session_state.recipes.get(selected_category, []):
        with st.container():
            st.subheader(recipe["title"])
            col1, col2 = st.columns([1, 2])
            if recipe.get("image") and os.path.exists(recipe["image"]):
                col1.image(recipe["image"], caption=recipe["title"], use_container_width=True)
            with col2:
                st.markdown(f"**Cooking Time:** {recipe['cooking_time']}")
                st.markdown(f"**Added by:** {recipe.get('user', 'Unknown')}")
                with st.expander("Ingredients"):
                    st.write("\n".join([f"- {ing}" for ing in recipe["ingredients"]]))
                with st.expander("Instructions"):
                    st.write(recipe["instructions"])
            if st.session_state.is_admin:
                if st.button(f"Delete {recipe['title']}", key=f"delete_{recipe['title']}"):
                    st.session_state.recipes[selected_category].remove(recipe)
                    save_recipes()
                    st.success(f"Recipe '{recipe['title']}' deleted successfully!")
                    st.experimental_rerun()
        st.markdown("---")

# Show the Add Recipe form
if st.session_state.get("show_add_recipe", False):
    st.header("Add a New Recipe")
    user = st.text_input("Your Name")
    title = st.text_input("Recipe Title")
    category = st.selectbox("Category", list(st.session_state.recipes.keys()))
    cooking_time = st.text_input("Cooking Time")
    ingredients = st.text_area("Ingredients (comma separated)")
    instructions = st.text_area("Instructions")
    image = st.file_uploader("Upload an Image", type=["jpg", "png", "jpeg"])

    if st.button("Add Recipe"):
        if not title or not cooking_time or not ingredients or not instructions or not user:
            st.warning("Please fill in all fields before adding the recipe.")
        else:
            new_recipe = {
                "title": title,
                "user": user,
                "cooking_time": cooking_time,
                "ingredients": [i.strip() for i in ingredients.split(",") if i.strip()],
                "instructions": instructions,
                "image": None
            }

            if image:
                image_path = os.path.join(IMAGE_DIR, image.name)
                with open(image_path, "wb") as f:
                    f.write(image.getbuffer())
                new_recipe["image"] = image_path

            if category not in st.session_state.recipes:
                st.session_state.recipes[category] = []

            st.session_state.recipes[category].append(new_recipe)
            save_recipes()
            st.success("Recipe added successfully!")
            st.session_state.show_add_recipe = False
            st.experimental_rerun()


