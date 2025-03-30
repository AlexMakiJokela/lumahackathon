import random
import os

images_list = [
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/Apsara5-2.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/Station-to-Station-1.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2023/01/lullaby-2000-e1675648047927.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/Aperture-2.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/FirstWorldProblemChild-2.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/Im-still-standin-2.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/Big-Sky-Mind-web.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/determination-1.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/02/Conjunction-of-Form-web-e1612383423367.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/Praise-the-Oontsa-Oontsa-1.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/tiananmansquare-1.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/Limits-web.jpg"
]

image_titles = {
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/Apsara5-2.jpg": "The Apsara & the Dragon #5",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/Station-to-Station-1.jpg": "Station to Station",
    "https://www.michaeldivine.com/wp-content/uploads/2023/01/lullaby-2000-e1675648047927.jpg": "Lullaby",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/Aperture-2.jpg": "Aperture",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/FirstWorldProblemChild-2.jpg": "First World Problem Child",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/Im-still-standin-2.jpg": "I'm Still Standing",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/Big-Sky-Mind-web.jpg": "Big Sky Mind",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/determination-1.jpg": "Determination",
    "https://www.michaeldivine.com/wp-content/uploads/2021/02/Conjunction-of-Form-web-e1612383423367.jpg": "Conjunction of Form",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/Praise-the-Oontsa-Oontsa-1.jpg": "Praise the Oontsa Oontsa",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/tiananmansquare-1.jpg": "Tiananmen Square",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/Limits-web.jpg": "Limits"
}

def get_top_image_for_emotion(emotion, images_emotions_dict):
    # Create a dictionary to store the maximum score for each URL
    scores = {url: emotions.get(emotion, 0) for url, emotions in images_emotions_dict.items()}
    
    # Find the highest score
    max_score = max(scores.values())
    
    # Filter the URLs that have the highest score
    top_images = [url for url, score in scores.items() if score == max_score]
    
    # Randomly select one of the top images if there is a tie
    chosen_image = random.choice(top_images)
    print(f"Image chosen for {emotion}: {chosen_image}")
    return chosen_image

def get_random_image():
    return random.choice(images_list)

# if __name__ == "__main__":
#     for image in images_list:
#         client = LumaAI(auth_token=os.getenv("LUMAAI_API_KEY"))

#         # Reference image URL and prompts for start and end keyframes
#         reference_image_weight= 0.95
#         start_prompt = f"draw a semi-abstract scene depicting profound feeling"

#         image_ref_object = [{
#         "url": image,
#         "weight": reference_image_weight
#         }]
#         try:
#             # Generate start keyframe
#             start_generation = client.generations.image.create(prompt=start_prompt, image_ref=image_ref_object)
#             start_keyframe_url = wait_until_generation_finishes(client, start_generation)
#             print(image,"SUCCESS")
#         except:
#             print(image,"FAILURE")