from flask import Flask, render_template, request, redirect, url_for, jsonify
import time
import requests
import os
import tempfile
import uuid
import traceback
import json
from luma_video_maker import make_a_heckin_video, extend_a_heckin_video
from images_list import get_random_image, get_top_image_for_emotion
from images_feels_dict import images_feels_dict

app = Flask(__name__)

# You'll need to set your Hume API key in environment variables for security
HUME_API_KEY = os.environ.get('HUME_API_KEY', "Tk7gEavEeErKMOlXMrmfZz2NAY4x3BofC0VlIWtw3G0GXmQA")

# Global variable to store the last set of sorted emotions
last_sorted_emotions = []
last_video_details = None
current_emotion_index = 2  # Start at index 2 since the first video uses emotions 0 and 1

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/output')
def output():
    video_history = request.args.get('video_history', '[]')
    
    try:
        # Parse video history
        video_history = json.loads(video_history)
    except json.JSONDecodeError:
        video_history = []
    
    return render_template('output.html', video_history=video_history)

@app.route('/extend_video', methods=['POST'])
def extend_video():
    """Endpoint to extend a video without requiring a new voice recording"""
    global last_sorted_emotions, last_video_details, current_emotion_index
    
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        previous_emotion = data.get('previous_emotion')
        emotion_index = int(data.get('emotion_index', current_emotion_index))
        
        if not previous_emotion:
            return jsonify({'error': 'Previous emotion is required'}), 400
            
        # Use the stored emotions from last recording
        if not last_sorted_emotions:
            return jsonify({'error': 'No emotions available. Please record your voice first.'}), 400
        
        # Use the next emotion in the list
        if emotion_index >= len(last_sorted_emotions):
            # If we've used all emotions, wrap around to the beginning
            emotion_index = emotion_index % len(last_sorted_emotions)
        
        # Log the emotion index and emotion being used
        print(f"Extending with emotion index: {emotion_index}, emotion: {last_sorted_emotions[emotion_index]['name']}")
        
        next_emotion = last_sorted_emotions[emotion_index]['name']
        
        # Reference image for extending
        reference_image = get_top_image_for_emotion(last_sorted_emotions[emotion_index]['name'], images_feels_dict)
        
        # Call extend_a_heckin_video with the next emotion
        video_details = extend_a_heckin_video(
            original_video_object=last_video_details,
            reference_image_url=reference_image,
            emotion=last_sorted_emotions[emotion_index]['name']
        )
        
        # Store the new video details for future extensions
        last_video_details = video_details
        
        # Increment the emotion index for the next extension
        current_emotion_index = emotion_index + 1
        
        # Extract and format text_block
        text_block = video_details.get("text_block", "No text block available")
        formatted_text = format_text_block(text_block)
        
        # Get video URL if available
        video_url = video_details.get("video_url", "")
        
        return jsonify({
            'emotion': next_emotion,
            'text_block': formatted_text,
            'video_url': video_url,
            'current_emotion_index': current_emotion_index
        })
        
    except Exception as e:
        print(f"Error extending video: {str(e)}")
        return jsonify({'error': f'Error extending video: {str(e)}'}), 500

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    global last_sorted_emotions, last_video_details, current_emotion_index
    
    # Reset the emotion index since we're starting a new recording
    current_emotion_index = 2  # Start at 2 because the first video uses emotions 0 and 1
    
    # Check if API key is set
    if not HUME_API_KEY:
        return jsonify({'error': 'Hume API key is not configured. Please set the HUME_API_KEY environment variable.'}), 500
        
    if 'audio_file' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio_file']
    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Create a temporary directory if it doesn't exist
    temp_dir = os.path.join(tempfile.gettempdir(), 'hume_audio')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate a unique ID for this recording
    file_id = str(uuid.uuid4())
    
    # Save the audio file
    audio_filename = f"HumeAI_artifacts_{file_id}.wav"
    audio_path = os.path.join(temp_dir, audio_filename)
    audio_file.save(audio_path)
    print(f"Audio saved to: {audio_path}")
    
    # Create a zip file for API submission
    zip_filename = f"HumeAI_artifacts_{file_id}.zip"
    zip_path = os.path.join(temp_dir, zip_filename)
    
    # Simple wrapper to create a zip file
    import zipfile
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        zip_file.write(audio_path, arcname=os.path.basename(audio_path))
    
    print(f"Zip file created at: {zip_path}")
    
    try:
        # Make the API request
        print("Making request to Hume API...")
        
        response = requests.post(
            "https://api.hume.ai/v0/batch/jobs",
            headers={
                "X-Hume-Api-Key": HUME_API_KEY
            },
            files=[
                ('file', (zip_filename, open(zip_path, 'rb')))
            ]
        )
        
        print(f"Hume API Response Status: {response.status_code}")
        print(f"Hume API Response: {response.text}")
        
        # Check for success
        if response.status_code == 200 or response.status_code == 201:
            # Extract the job ID from the response
            response_data = response.json()
            job_id = response_data.get('job_id')
            
            if job_id:
                # Poll for job status
                job_status_url = f"https://api.hume.ai/v0/batch/jobs/{job_id}"
                job_status = "IN_PROGRESS"
                max_retries = 15
                retries = 0
                
                while job_status in ["IN_PROGRESS", "PENDING", "QUEUED"] and retries < max_retries:
                    time.sleep(2)  # Wait before polling again
                    job_status_response = requests.get(
                        job_status_url,
                        headers={"X-Hume-Api-Key": HUME_API_KEY}
                    )
                    
                    if job_status_response.status_code == 200:
                        job_status_data = job_status_response.json()
                        
                        # Handle nested structure: state -> status
                        if 'state' in job_status_data and isinstance(job_status_data['state'], dict):
                            job_status = job_status_data['state'].get('status')
                        else:
                            job_status = job_status_data.get('status')
                            
                        print(f"Job status: {job_status}")
                        
                        # If job is complete, get the results
                        if job_status == "COMPLETED" or job_status == "SUCCESS":
                            job_results_url = f"https://api.hume.ai/v0/batch/jobs/{job_id}/predictions"
                            job_results_response = requests.get(
                                job_results_url,
                                headers={"X-Hume-Api-Key": HUME_API_KEY}
                            )
                            
                            if job_results_response.status_code == 200:
                                results_data = job_results_response.json()
                                
                                try:
                                    # Extract emotions from results
                                    def find_emotions(data):
                                        if isinstance(data, dict):
                                            if 'emotions' in data and isinstance(data['emotions'], list) and len(data['emotions']) > 0:
                                                return data['emotions']
                                            for key, value in data.items():
                                                result = find_emotions(value)
                                                if result:
                                                    return result
                                        elif isinstance(data, list):
                                            for item in data:
                                                result = find_emotions(item)
                                                if result:
                                                    return result
                                        return None
                                    
                                    emotions = find_emotions(results_data)
                                    if emotions:
                                        # Sort emotions by score
                                        sorted_emotions = sorted(emotions, key=lambda x: x.get('score', 0), reverse=True)
                                        
                                        # Save the sorted emotions for later use
                                        last_sorted_emotions = sorted_emotions
                                        
                                        # Log all detected emotions
                                        print(f"All detected emotions: {[e.get('name') for e in sorted_emotions]}")
                                        
                                        # Get the top emotions for display
                                        emotion_name = ""
                                        for x in range(min(2, len(sorted_emotions))):
                                            top_emotion = sorted_emotions[x]
                                            emotion_name = emotion_name + " to " + top_emotion.get('name', 'unknown')
                                        
                                        emotion_name = emotion_name.strip()
                                        
                                        # Get reference images for the video generation
                                        reference_image_url_start = get_top_image_for_emotion(sorted_emotions[0]["name"], images_feels_dict)
                                        reference_image_url_end =get_top_image_for_emotion(sorted_emotions[1]["name"], images_feels_dict)
                                        
                                        # Create a new video
                                        print(f"Creating new video with emotions: {sorted_emotions[0]['name']} and {sorted_emotions[1]['name'] if len(sorted_emotions) > 1 else sorted_emotions[0]['name']}")
                                        video_details = make_a_heckin_video(
                                            reference_image_url_start=reference_image_url_start,
                                            reference_image_url_end=reference_image_url_end,
                                            emotion1=sorted_emotions[0]["name"],
                                            emotion2=sorted_emotions[1]["name"] if len(sorted_emotions) > 1 else sorted_emotions[0]["name"]
                                        )
                                        
                                        # Save video details for future extensions
                                        last_video_details = video_details
                                        
                                        # Extract text_block from video_details
                                        text_block = video_details.get("text_block", "No text block available")
                                        
                                        # Get video URL if available
                                        video_url = video_details.get("video_url", "")
                                        
                                        # Format text_block for better readability
                                        formatted_text = format_text_block(text_block)
                                        
                                        # Return both the emotion and the text_block, along with all emotions detected
                                        return jsonify({
                                            'emotion': emotion_name, 
                                            'text_block': formatted_text,
                                            'video_url': video_url,
                                            'all_emotions': [e.get('name') for e in sorted_emotions],
                                            'current_emotion_index': current_emotion_index
                                        })
                                    
                                    # Default if no emotions found
                                    return jsonify({
                                        'emotion': 'neutral',
                                        'text_block': 'No emotions were detected in your voice. Please try again and speak clearly about how you feel.'
                                    })
                                except Exception as e:
                                    stack_trace = traceback.format_exc()
                                    
                                    # Print the full stack trace to the console
                                    print(f"Error processing results: {str(e)}")
                                    print(f"Stack trace:\n{stack_trace}")
                                    return jsonify({'error': f'Error processing results: {str(e)}'}), 500
                            else:
                                return jsonify({'error': f'Error getting job results: {job_results_response.status_code}'}), 500
                    else:
                        print(f"Error checking job status: {job_status_response.status_code}")
                    
                    retries += 1
                
                if retries >= max_retries:
                    # If we hit max retries but the job is still in progress, return a temporary emotion
                    if job_status == "IN_PROGRESS":
                        print("Job still in progress but returning provisional result")
                        return jsonify({
                            'emotion': 'neutral', 
                            'text_block': 'Analysis still in progress. Please wait a moment and try again.',
                            'note': 'Analysis still in progress'
                        })
                    else:
                        return jsonify({'error': 'Job took too long to complete'}), 500
                
                # If job failed with some other status
                print(f"Job failed or returned unexpected status: {job_status}")
                return jsonify({'error': f'Job failed with status: {job_status}'}), 500
            else:
                return jsonify({'error': 'No job ID in response'}), 500
        else:
            return jsonify({'error': f'Hume API error: {response.status_code} - {response.text}'}), response.status_code
    
    except Exception as e:
        print(f"Error connecting to Hume API: {str(e)}")
        return jsonify({'error': f'Error connecting to Hume API: {str(e)}'}), 500
    finally:
        # Clean up the files
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
            if os.path.exists(zip_path):
                os.remove(zip_path)
        except Exception as cleanup_error:
            print(f"Error cleaning up files: {str(cleanup_error)}")

def format_text_block(text):
    """Format the text block for better readability"""
    if not text:
        return "No description available."
    
    # Ensure proper paragraph breaks
    formatted_text = text.replace('\n\n', '\n').replace('\n\n\n', '\n\n')
    
    # Add section titles if not present
    if "Scene Description:" not in formatted_text:
        sections = formatted_text.split('\n\n')
        if len(sections) >= 3:
            formatted_text = "Video Overview:\n" + sections[0] + "\n\n"
            formatted_text += "Scene Description:\n" + sections[1] + "\n\n"
            formatted_text += "Emotional Journey:\n" + '\n\n'.join(sections[2:])
    
    return formatted_text

if __name__ == '__main__':
    app.run(debug=True)