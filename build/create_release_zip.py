import zipfile
import os
import datetime
import shutil

def create_zip():
    # Get script directory and set paths relative to project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    # Get version from pyproject.toml
    version = "unknown"
    try:
        pyproject_path = os.path.join(project_dir, 'pyproject.toml')
        if os.path.exists(pyproject_path):
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith('version = '):
                        version = line.split('=')[1].strip().strip('"').strip("'")
                        break
    except Exception as e:
        print(f"Warning: Could not read version: {e}")

    now = datetime.datetime.now()
    datestamp = now.strftime('%Y%m%d_%H%M%S')
    zip_filename = f'dify_chat_tester_windows_v{version}_{datestamp}.zip'
    
    source_dir = os.path.join(project_dir, 'release_windows')
    zip_path = os.path.join(project_dir, zip_filename)
    
    print(f"Script dir: {script_dir}")
    print(f"Project dir: {project_dir}")
    print(f"Source dir: {source_dir}")
    print(f"Zip path: {zip_path}")
    
    # Always create release directory and copy files
    print("Creating release directory and copying files...")
    os.makedirs(source_dir, exist_ok=True)
    
    # Copy files to release directory
    dist_dir = os.path.join(project_dir, 'dist')
    exe_file = os.path.join(dist_dir, 'dify_chat_tester.exe')
    
    # Copy executable
    if os.path.exists(exe_file):
        shutil.copy2(exe_file, os.path.join(source_dir, 'dify_chat_tester.exe'))
        print("Copied executable")
    
    # Copy config template
    config_file = os.path.join(project_dir, '.env.config.example')
    if os.path.exists(config_file):
        shutil.copy2(config_file, os.path.join(source_dir, '.env.config.example'))
        print("Copied config template")
    
    # Copy Excel template
    excel_file = os.path.join(project_dir, 'dify_chat_tester_template.xlsx')
    if os.path.exists(excel_file):
        shutil.copy2(excel_file, os.path.join(source_dir, 'dify_chat_tester_template.xlsx'))
        print("Copied Excel template")
    
    # Copy README
    readme_file = os.path.join(project_dir, 'README.md')
    if os.path.exists(readme_file):
        shutil.copy2(readme_file, os.path.join(source_dir, 'README.md'))
        print("Copied README")
    
    # Copy docs folder
    docs_dir = os.path.join(project_dir, 'docs')
    if os.path.exists(docs_dir):
        shutil.copytree(docs_dir, os.path.join(source_dir, 'docs'), dirs_exist_ok=True)
        print("Copied docs folder")
    
    # Create ZIP
    print(f"Creating ZIP archive: {zip_filename}")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")
    
    print(f'Successfully created {zip_filename}')
    return True

if __name__ == '__main__':
    create_zip()