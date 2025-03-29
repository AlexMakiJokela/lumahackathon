import os
import time
from lumaai import LumaAI



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
start_prompt = "draw an office scene in the style of the reference image"
end_prompt = "draw an airport scene in the style of the reference image"

image_ref_object = [{
  "url": reference_image_url,
  "weight": 0.5
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
    "url": reference_image_url
}
end_keyframe = {
    "type": "image",
    "url": end_keyframe_url
}
prompt = "idk bro make it vibe sad"

# Create the video generation
generation = client.generations.create(
    aspect_ratio="16:9",
    model="ray-2",
    loop=False,
    prompt=prompt,
    keyframes={"frame0": start_keyframe, "frame1": end_keyframe}
)

completed = False
while not completed:
  generation = client.generations.get(id=generation.id)
  if generation.state == "completed":
    completed = True
  elif generation.state == "failed":
    raise RuntimeError(f"Generation failed: {generation.failure_reason}")
  print("Dreaming")
  time.sleep(3)

# Print the URL to view the video
print(f"View your video here: {generation.assets.video}")

