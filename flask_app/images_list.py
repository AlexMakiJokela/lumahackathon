import random
import os
from luma_video_maker import LumaAI, wait_until_generation_finishes

images_list = [
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/Apsara5-2.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/Station-to-Station-1.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/02/IMG_20200715_101510.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2023/01/lullaby-2000-e1675648047927.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/Aperture-2.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/FirstWorldProblemChild-2.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/Im-still-standin-2.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/Big-Sky-Mind-web.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/determination-1.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/02/Conjunction-of-Form-web-e1612383423367.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/Praise-the-Oontsa-Oontsa-1.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/tiananmansquare-1.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/birthofastar-sm2.jpg",
    "https://www.michaeldivine.com/wp-content/uploads/2021/01/Limits-web.jpg"
]


images_emotions_dict = {}

images_emotions_dict["https://www.michaeldivine.com/wp-content/uploads/2021/01/Station-to-Station-1.jpg"] = {
    "Admiration": 0.78, "Adoration": 0.24, "Aesthetic Appreciation": 0.92, "Amusement": 0.12, "Anger": 0.00,
    "Annoyance": 0.00, "Anxiety": 0.10, "Awe": 0.88, "Awkwardness": 0.00, "Boredom": 0.00,
    "Calmness": 0.54, "Concentration": 0.22, "Confusion": 0.15, "Contemplation": 0.45, "Contempt": 0.00,
    "Contentment": 0.58, "Craving": 0.00, "Desire": 0.08, "Determination": 0.18, "Disappointment": 0.00,
    "Disapproval": 0.00, "Disgust": 0.00, "Distress": 0.04, "Doubt": 0.12, "Ecstasy": 0.14,
    "Embarrassment": 0.00, "Empathic Pain": 0.00, "Enthusiasm": 0.36, "Entrancement": 0.82, "Envy": 0.00,
    "Excitement": 0.37, "Fear": 0.09, "Gratitude": 0.00, "Guilt": 0.00, "Horror": 0.00,
    "Interest": 0.76, "Joy": 0.34, "Love": 0.25, "Nostalgia": 0.19, "Pain": 0.00,
    "Pride": 0.20, "Realization": 0.11, "Relief": 0.00, "Romance": 0.23, "Sadness": 0.00,
    "Sarcasm": 0.00, "Satisfaction": 0.59, "Shame": 0.00, "Surprise (negative)": 0.00, "Surprise (positive)": 0.21,
    "Sympathy": 0.00, "Tiredness": 0.00, "Triumph": 0.00
}


def get_top_image_for_emotion(emotion, images_emotions_dict):
    # Create a dictionary to store the maximum score for each URL
    scores = {url: emotions.get(emotion, 0) for url, emotions in images_emotions_dict.items()}
    
    # Find the highest score
    max_score = max(scores.values())
    
    # Filter the URLs that have the highest score
    top_images = [url for url, score in scores.items() if score == max_score]
    
    # Randomly select one of the top images if there is a tie
    return random.choice(top_images)

def get_random_image():
    return random.choice(images_list)

if __name__ == "__main__":
    for image in images_list:
        client = LumaAI(auth_token=os.getenv("LUMAAI_API_KEY"))

        # Reference image URL and prompts for start and end keyframes
        reference_image_weight= 0.95
        start_prompt = f"draw a semi-abstract scene depicting profound feeling"

        image_ref_object = [{
        "url": image,
        "weight": reference_image_weight
        }]
        try:
            # Generate start keyframe
            start_generation = client.generations.image.create(prompt=start_prompt, image_ref=image_ref_object)
            start_keyframe_url = wait_until_generation_finishes(client, start_generation)
            print(image,"SUCCESS")
        except:
            print(image,"FAILURE")