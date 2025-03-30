import os
import time
import random
from lumaai import LumaAI
from emotions_list import emotions_list
from images_list import image_titles


emotion1=random.choice(emotions_list)
emotion2=random.choice(emotions_list)
reference_image_url_start = "https://www.michaeldivine.com/wp-content/uploads/2021/01/Apsara5-2.jpg"
reference_image_url_end = "https://www.michaeldivine.com/wp-content/uploads/2021/01/Station-to-Station-1.jpg"

def wait_until_generation_finishes(client, start_generation):
    completed = False
    while not completed:
      generation = client.generations.get(id=start_generation.id)
      if generation.state == "completed":
        completed = True
      elif generation.state == "failed":
        print(generation)
        raise RuntimeError(f"Generation failed: {generation.failure_reason}")
      print("Dream state:", generation.state)
      time.sleep(2)
    return generation.assets.image


def make_a_heckin_video(reference_image_url_start, reference_image_url_end, emotion1, emotion2): 
    # Initialize the LumaAI client
    client = LumaAI(auth_token=os.getenv("LUMAAI_API_KEY"))

    # Reference image URL and prompts for start and end keyframes
    reference_image_weight= 0.95
    start_prompt = f"draw a semi-abstract scene depicting profound {emotion1}"
    end_prompt = f"draw a semi-abstract scene depicting profound {emotion2}"

    image_ref_object = [{
    "url": reference_image_url_start,
    "weight": reference_image_weight
    }]

    # Generate start keyframe
    start_generation = client.generations.image.create(prompt=start_prompt, image_ref=image_ref_object)
    start_keyframe_url = wait_until_generation_finishes(client, start_generation)

    last_keyframe_image_ref_based_on_first_keyframe= [{
    "url": reference_image_url_end,
    "weight": 0.75
    },{"url": start_keyframe_url,
    "weight": 0.6}]

    transform_first_keyframe_prompt = f"transform the reference image into a semi-abstract scene depicting profound {emotion2}"

    # Generate end keyframe
    end_generation = client.generations.image.create(prompt=transform_first_keyframe_prompt, image_ref=last_keyframe_image_ref_based_on_first_keyframe)
    end_keyframe_url = wait_until_generation_finishes(client, end_generation)

    # Define the start and end keyframes and prompt
    start_keyframe = {
        "type": "image",
        "url": start_keyframe_url
    }
    end_keyframe = {
        "type": "image",
        "url": end_keyframe_url
    }
    video_prompt = f"draw a smooth, dreamy transition that swirl and evolves from a semi-abstract scene depicting profound {emotion1} to a  semi-abstract scene depicting profound {emotion2}, high detail, detail evolves intricately and dynamically over time"

    # Create the video generation
    generation = client.generations.create(
        aspect_ratio="16:9",
        model="ray-2",
        loop=False,
        prompt=video_prompt,
        keyframes={"frame0": start_keyframe, "frame1": end_keyframe}
    )

    completed = False
    while not completed:
        generation = client.generations.get(id=generation.id)
        if generation.state == "completed":
            completed = True
        elif generation.state == "failed":
            raise RuntimeError(f"Generation failed: {generation.failure_reason}")
        print(f"Dreaming ur heckin video and the api is all like homie be patient I'm {generation.state}")
        time.sleep(3)

    # Print the URL to view the video
    print(f"Start reference image url: {reference_image_url_start}, weight {reference_image_weight}")
    print(f"End reference image url: {reference_image_url_end}")
    print(f"Emotional transition: {emotion1} to {emotion2}")
    print(f"Start keyrame prompt: {start_prompt}")
    print(f"End keyrame prompt: {end_prompt}")
    print(f"Video prompt: {video_prompt}")
    print(f"View your video here: {generation.assets.video}")

    # Building the dictionary
    video_details = {
        'reference_image_start_url': reference_image_url_start,
        'reference_image_end_url': reference_image_url_end,
        'reference_image_start_title': image_titles[reference_image_url_start],
        'reference_image_end_title': image_titles[reference_image_url_end],
        'emotion1': emotion1,
        'emotion2': emotion2,
        'start_prompt': start_prompt,
        'end_prompt': end_prompt,
        'start_keyframe_url': start_keyframe_url,
        'end_keyframe_url': end_keyframe_url,
        'video_prompt': video_prompt,
        'video_url': generation.assets.video,
        'text_block': (
            f"Reference image url start: {reference_image_url_start}\n"
            f"Reference image url end: {reference_image_url_end}\n"
            f"Reference image title start: {image_titles[reference_image_url_start]}\n"
            f"Reference image title end: {image_titles[reference_image_url_end]}\n"
            f"Emotional transition: {emotion1} to {emotion2}\n"
            f"Start keyframe prompt: {start_prompt}\n"
            f"End keyframe prompt: {end_prompt}\n"
            f"Video prompt: {video_prompt}\n"
            f"View your video here: {generation.assets.video}"
        ),
        "generation": generation
    }

    print(video_details["text_block"])

    return video_details

def extend_a_heckin_video(original_video_object,emotion,reference_image_url):
    client = LumaAI(auth_token=os.getenv("LUMAAI_API_KEY"))

    next_keyframe_image_ref_based_on_last_keyframe= [{
    "url": reference_image_url,
    "weight": 0.75
    },{"url": original_video_object["end_keyframe_url"],
    "weight": 0.55}]

    transform_to_next_keyframe_prompt = f"transform the reference image into a  semi-abstract scene depicting profound {emotion}"

    # Generate end keyframe
    next_generation = client.generations.image.create(prompt=transform_to_next_keyframe_prompt, image_ref=next_keyframe_image_ref_based_on_last_keyframe)
    next_keyframe_url = wait_until_generation_finishes(client, next_generation)

    video_prompt = f"draw a smooth, dreamy transition that swirl and evolves towards a semi-abstract scene depicting profound {emotion}, high detail, detail evolves intricately and dynamically over time"

    generation = client.generations.create(
        prompt=video_prompt,
        keyframes={
        "frame0": {
            "type": "generation",
            "id": original_video_object["generation"].id
        },
        "frame1": {
            "type": "image",
            "url": next_keyframe_url
        }
        }
    )
    completed = False
    while not completed:
        generation = client.generations.get(id=generation.id)
        if generation.state == "completed":
            completed = True
        elif generation.state == "failed":
            raise RuntimeError(f"Generation failed: {generation.failure_reason}")
        print(f"Dreaming ur heckin video and the api is all like homie be patient I'm {generation.state}")
        time.sleep(3)

    # Print the URL to view the video
    print(f"Reference image url: {reference_image_url}")
    print(f"Emotional transition: now to {emotion}")
    print(f"New keyrame prompt: {transform_to_next_keyframe_prompt}")
    print(f"Video prompt: {video_prompt}")
    print(f"View your video here: {generation.assets.video}")

    # Building the dictionary
    video_details = {
        'reference_image_url': reference_image_url,
        'reference_image_end_url': reference_image_url_end,
        'reference_image_end_title': image_titles[reference_image_url],
        'emotion': emotion,
        'end_prompt': transform_to_next_keyframe_prompt,
        'end_keyframe_url': next_keyframe_url,
        'video_prompt': video_prompt,
        'video_url': generation.assets.video,
        'text_block': (
            f"Reference image url end: {reference_image_url}\n"
            f"Reference image title end: {image_titles[reference_image_url]}\n"
            f"Emotional transition: {emotion}\n"
            f"End keyframe prompt: {transform_to_next_keyframe_prompt}\n"
            f"Video prompt: {video_prompt}\n"
            f"View your video here: {generation.assets.video}"
        ),
        'original_video_object': original_video_object,
        "generation": generation
    }

    print(video_details["text_block"])
    print(video_details)

    return video_details



if __name__ == '__main__':
    emotion1=random.choice(emotions_list)
    emotion2=random.choice(emotions_list)
    reference_image_url_start = "https://www.michaeldivine.com/wp-content/uploads/2021/01/Apsara5-2.jpg"
    reference_image_url_end = "https://www.michaeldivine.com/wp-content/uploads/2021/01/Station-to-Station-1.jpg"
    first_video_object=make_a_heckin_video(reference_image_url_start=reference_image_url_start,
                        reference_image_url_end=reference_image_url_end,
                        emotion1=emotion1,
                        emotion2=emotion2)
    emotion3=random.choice(emotions_list)
    reference_image_3 = "https://www.michaeldivine.com/wp-content/uploads/2021/02/IMG_20200715_101510.jpg"
    extend_a_heckin_video(first_video_object, emotion3, reference_image_3)
