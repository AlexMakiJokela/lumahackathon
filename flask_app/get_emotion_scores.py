"""
Get emotion scores on fixed images_list

Put Groq API key into environment variable.

You can run this in the command line:

export GROQ_API_KEY=<your_groq_api_key>
"""

from import_in_groq import add_groq_to_path
add_groq_to_path()

from moregroq.Tools.EmotionScorer import (
    score_image_emotion,
)
from moregroq.Wrappers import GroqAPIWrapper

from images_list import images_list
from emotions_list import emotions_list

import os
import json
from tqdm import tqdm
import time
from pathlib import Path

# Hardcoded filename for the emotion scores cache
EMOTION_SCORES_FILE = "emotion_scores.json"

def save_emotion_scores(scores_dict, filename=EMOTION_SCORES_FILE):
    """Save emotion scores dictionary to a JSON file"""
    print(f"\nSaving emotion scores to {filename}...")
    
    with open(filename, 'w') as f:
        json.dump(scores_dict, f, indent=2)
    
    print(f"✅ Saved emotion scores for {len(scores_dict)} images to {filename}")
    return filename

def get_emotion_scores():
    """
    Get emotion scores on fixed images_list
    
    Returns:
        Dictionary of emotion scores for each image
    """
    # Initialize the Groq API wrapper
    groq_api_wrapper = GroqAPIWrapper(api_key=os.environ.get('GROQ_API_KEY'))
#    groq_api_wrapper.configuration.model = "llama-3.2-90b-vision-preview"
    groq_api_wrapper.configuration.model = "llama-3.2-11b-vision-preview"
    groq_api_wrapper.configuration.stream = False
    groq_api_wrapper.configuration.temperature = 0.5
    groq_api_wrapper.configuration.max_completion_tokens = 1024

    image_emotion_score_dict = {}
    
    # Create outer progress bar for images
    print(f"Analyzing {len(images_list)} images for {len(emotions_list)} emotions each..")
    
    for i, image_url in enumerate(tqdm(images_list, desc="Images", ncols=100)):
        # Extract filename or use shortened URL for display
        image_name = image_url.split('/')[-1][:20] + "..." if len(image_url) > 30 else image_url
        print(f"\nImage {i+1}/{len(images_list)}: {image_name}")
        
        emotion_scores = {}
        
        # Create inner progress bar for emotions
        for emotion in tqdm(emotions_list, desc="Emotions", leave=False, ncols=100):
            # Add a small delay to make the progress visible
            start_time = time.time()
            
            # Score the emotion
            result = score_image_emotion(groq_api_wrapper, image_url, emotion)
            emotion_scores[emotion] = result.score
            
            elapsed = time.time() - start_time
            print(f"  - {emotion}: {result.score:.2f} ({elapsed:.1f}s)")
        
        # Add summary for this image
        top_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        print(f"✓ Image {i+1} complete. Top emotion: {top_emotion[0]} ({top_emotion[1]:.2f})")
        
        image_emotion_score_dict[image_url] = emotion_scores
        
        # Save the intermediate results after each image
        save_emotion_scores(image_emotion_score_dict)

    print(f"\n✅ All {len(images_list)} images analyzed successfully!")
    return image_emotion_score_dict


if __name__ == "__main__":
    # Get emotion scores
    image_emotion_score_dict = get_emotion_scores()

    # Print the entire dictionary
    print("\n\nENTIRE EMOTION SCORES DICTIONARY:")
    print(json.dumps(image_emotion_score_dict, indent=2))

    # Save to file (this is already done in get_emotion_scores, but just to be explicit)
    saved_file = save_emotion_scores(image_emotion_score_dict)
    
    print("\nFINAL RESULTS:")
    
    # Print a summary of the results
    for i, (image_url, emotions) in enumerate(image_emotion_score_dict.items()):
        image_name = image_url.split('/')[-1]
        print(f"\nImage {i+1}: {image_name}")
        
        # Sort emotions by score (highest first)
        sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
        
        # Print top 3 emotions
        for j, (emotion, score) in enumerate(sorted_emotions[:3]):
            print(f"  {j+1}. {emotion}: {score:.2f}")   
    
    print(f"\nResults are cached in {saved_file} for future use.")
