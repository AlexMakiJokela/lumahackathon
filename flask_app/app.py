from flask import Flask, render_template, request, redirect, url_for, jsonify
import time
import requests
import gzip
import os
import tempfile
import uuid

app = Flask(__name__)

# You'll need to set your Hume API key in environment variables for security
HUME_API_KEY = os.environ.get('HUME_API_KEY', "Tk7gEavEeErKMOlXMrmfZz2NAY4x3BofC0VlIWtw3G0GXmQA")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        image_url = request.form.get('image_url')
        effects_text = request.form.get('effects_text')
        scenes_text = request.form.get('scenes_text')
        voice_emotion = request.form.get('voice_emotion')
        
        # Here is where you would process the inputs.
        # Simulating processing delay:
        time.sleep(3)  # Simulate a long generation process
        
        # After processing, redirect to the output page.
        return redirect(url_for('output',
                                image_url=image_url,
                                effects_text=effects_text,
                                scenes_text=scenes_text,
                                voice_emotion=voice_emotion))
    return render_template('index.html')

@app.route('/output')
def output():
    image_url = request.args.get('image_url')
    effects_text = request.args.get('effects_text')
    scenes_text = request.args.get('scenes_text')
    voice_emotion = request.args.get('voice_emotion')
    return render_template('output.html',
                          image_url=image_url,
                          effects_text=effects_text,
                          scenes_text=scenes_text,
                          voice_emotion=voice_emotion)

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
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
    
    # Create a zip file if needed (you might not need this step if your API accepts WAV directly)
    zip_filename = f"HumeAI_artifacts_{file_id}.zip"
    zip_path = os.path.join(temp_dir, zip_filename)
    
    # Simple wrapper to create a zip file
    import zipfile
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        zip_file.write(audio_path, arcname=os.path.basename(audio_path))
    
    print(f"Zip file created at: {zip_path}")
    
    try:
        # Make the API request exactly as in the example
        print("Making request to Hume API...")
        
        # Fix: Don't manually set Content-Type for multipart/form-data
        # The requests library will set it automatically with the correct boundary
        response = requests.post(
            "https://api.hume.ai/v0/batch/jobs",
            headers={
                "X-Hume-Api-Key": HUME_API_KEY
                # Remove the Content-Type header - requests will set it automatically
            },
            files=[
                ('file', (zip_filename, open(zip_path, 'rb')))
            ]
        )
        
        print(f"Hume API Response Status: {response.status_code}")
        print(f"Hume API Response Headers: {response.headers}")
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
                max_retries = 15  # Increased for longer processing time
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
                        print(f"Full job status data: {job_status_data}")
                        
                        # If job is complete, get the results
                        if job_status == "COMPLETED" or job_status == "SUCCESS":
                            job_results_url = f"https://api.hume.ai/v0/batch/jobs/{job_id}/predictions"
                            job_results_response = requests.get(
                                job_results_url,
                                headers={"X-Hume-Api-Key": HUME_API_KEY}
                            )
                            
                            if job_results_response.status_code == 200:
                                results_data = job_results_response.json()
                                print(f"Job results: {results_data}")
                                
                                # Process results to extract emotion
                                # This is simplified - adjust based on actual response structure
                                try:
                                    # Print the structure to understand the format
                                    print("Results data structure:", results_data)
                                    
                                    # More flexible extraction of emotion data
                                    # First try to extract based on expected format
                                    if 'predictions' in results_data:
                                        predictions = results_data.get('predictions', [])
                                        if predictions and len(predictions) > 0:
                                            # Try to find prosody predictions
                                            for prediction in predictions:
                                                if isinstance(prediction, dict) and 'prosody' in prediction:
                                                    emotions = prediction['prosody'].get('emotions', [])
                                                    if emotions and len(emotions) > 0:
                                                        # Sort emotions by score
                                                        sorted_emotions = sorted(emotions, key=lambda x: x.get('score', 0), reverse=True)
                                                        top_emotion = sorted_emotions[0]
                                                        emotion_name = top_emotion.get('name', 'unknown')
                                                        return jsonify({'emotion': emotion_name})
                                    
                                    # Alternative formats to try
                                    # Directly try to find emotions data
                                    if 'prosody' in results_data:
                                        emotions = results_data['prosody'].get('emotions', [])
                                        if emotions and len(emotions) > 0:
                                            sorted_emotions = sorted(emotions, key=lambda x: x.get('score', 0), reverse=True)
                                            top_emotion = sorted_emotions[0]
                                            emotion_name = top_emotion.get('name', 'unknown')
                                            return jsonify({'emotion': emotion_name})
                                    
                                    # Fallback - search for any 'emotions' key in the response
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
                                        sorted_emotions = sorted(emotions, key=lambda x: x.get('score', 0), reverse=True)
                                        emotion_name=""
                                        for x in range(0,3):
                                            top_emotion = sorted_emotions[x]
                                            emotion_name = emotion_name + " " + top_emotion.get('name', 'unknown')
                                        return jsonify({'emotion': emotion_name})
                                    
                                    # Default if no emotions found
                                    return jsonify({'emotion': 'neutral'})
                                except Exception as e:
                                    print(f"Error processing results: {str(e)}")
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
                        return jsonify({'emotion': 'neutral', 'note': 'Analysis still in progress'})
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

if __name__ == '__main__':
    app.run(debug=True)