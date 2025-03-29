import os
import time
from lumaai import LumaAI

emotion1="Sadness"
emotion2="Determination"

def wait_until_generation_finishes(client, start_generation):
    completed = False
    while not completed:
      generation = client.generations.get(id=start_generation.id)
      if generation.state == "completed":
        completed = True
      elif generation.state == "failed":
        raise RuntimeError(f"Generation failed: {start_generation.failure_reason}")
      print("Dream state:", generation.state)
      time.sleep(2)
    return generation.assets.image

# Initialize the LumaAI client
client = LumaAI(auth_token=os.getenv("LUMAAI_API_KEY"))

# Reference image URL and prompts for start and end keyframes
reference_image_url = "https://www.michaeldivine.com/wp-content/uploads/2021/01/Station-to-Station-1.jpg"
reference_image_weight= 0.75
start_prompt = f"draw a semi-abstract scene depicting profound {emotion1}"
end_prompt = f"draw a semi-abstract scene depicting profound {emotion2}"

image_ref_object = [{
  "url": reference_image_url,
  "weight": reference_image_weight
}]

# Generate start keyframe
start_generation = client.generations.image.create(prompt=start_prompt, image_ref=image_ref_object)
start_keyframe_url = wait_until_generation_finishes(client, start_generation)

# Generate end keyframe
end_generation = client.generations.image.create(prompt=end_prompt, image_ref=image_ref_object)
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
video_prompt = f"draw abstract scenes with the feeling shifting from profound {emotion1} to profound {emotion2}"

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
  print("Dreaming ur heckin video")
  time.sleep(3)

# Print the URL to view the video
print(f"Reference image url: {reference_image_url}, weight {reference_image_weight}")
print(f"Emotional transition: {emotion1} to {emotion2}")
print(f"Start keyrame prompt: {start_prompt}")
print(f"End keyrame prompt: {end_prompt}")
print(f"Video prompt: {video_prompt}")
print(f"View your video here: {generation.assets.video}")

