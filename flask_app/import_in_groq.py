import sys
from pathlib import Path

def add_groq_to_path():
    """
    Add the MoreGroq module to sys.path
    This allows importing MoreGroq in the application
    """
    # Get the absolute path of this file
    current_file = Path(__file__).resolve()
    
    # Get the flask_app directory
    flask_app_dir = current_file.parent
    
    # Get the parent of flask_app directory (project root)
    project_root = flask_app_dir.parent
    
    # Construct path to MoreGroq
    groq_path = project_root / "PythonLibraries" / "ThirdParties" / "APIs" / "MoreGroq"
    
    # Add to sys.path if not already present
    groq_path_str = str(groq_path)
    if groq_path_str not in sys.path:
        sys.path.append(groq_path_str)
        print(f"Added to sys.path: {groq_path_str}")
    
    return groq_path_str

# This enables using the function as a module
if __name__ == "__main__":
    add_groq_to_path()
