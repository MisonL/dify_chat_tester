import zipfile
import os
import datetime

def create_zip():
    now = datetime.datetime.now()
    datestamp = now.strftime('%Y%m%d_%H%M%S')
    zip_filename = f'dify_chat_tester_windows_{datestamp}.zip'
    
    # Get script directory and set paths relative to project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    source_dir = os.path.join(project_dir, 'release_windows')
    zip_path = os.path.join(project_dir, zip_filename)
    
    if not os.path.exists(source_dir):
        print(f"Error: Source directory '{source_dir}' not found")
        return False
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
    
    print(f'Created {zip_filename}')
    return True

if __name__ == '__main__':
    create_zip()