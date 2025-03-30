"""
Get emotion scores on fixed images_list
"""

from import_in_groq import add_groq_to_path
add_groq_to_path()

from moregroq.Tools.EmotionScorer import (
    score_image_emotion,
)
from moregroq.Wrappers import GroqAPIWrapper

from images_list import images_list
from emotions_list import emotions_list

def get_emotion_scores():
    """
    Get emotion scores on fixed images_list
    """
    groq_api_wrapper = GroqAPIWrapper(api_key=os.environ.get('GROQ_API_KEY'))
    groq_api_wrapper.configuration.model = "llama-3.2-90b-vision-preview"
    groq_api_wrapper.configuration.stream = False
    groq_api_wrapper.configuration.temperature = 0.5
    groq_api_wrapper.configuration.max_completion_tokens = 1024

    image_emotion_score_dict = {}

    for image_url in images_list:
        emotion_scores = {}

        for emotion in emotions_list:
            result = score_image_emotion(groq_api_wrapper, image_url, emotion)
            emotion_scores[emotion] = result.score

        image_emotion_score_dict[image_url] = emotion_scores

    return image_emotion_score_dict


if __name__ == "__main__":
    image_emotion_score_dict = get_emotion_scores()
    print(image_emotion_score_dict)
