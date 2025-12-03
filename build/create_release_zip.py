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
        print(f"警告: 无法读取版本号: {e}")

    now = datetime.datetime.now()
    datestamp = now.strftime('%Y%m%d_%H%M%S')
    zip_filename = f'dify_chat_tester_windows_v{version}_{datestamp}.zip'
    
    source_dir = os.path.join(project_dir, 'release_windows')
    zip_path = os.path.join(project_dir, zip_filename)
    
    print(f"脚本目录: {script_dir}")
    print(f"项目目录: {project_dir}")
    print(f"发布目录: {source_dir}")
    print(f"压缩包路径: {zip_path}")
    
    # Always create release directory and copy files
    print("创建发布目录并复制文件...")
    os.makedirs(source_dir, exist_ok=True)
    
    # Copy files to release directory
    dist_dir = os.path.join(project_dir, 'dist')
    exe_file = os.path.join(dist_dir, 'dify_chat_tester.exe')
    
    # Copy executable
    if os.path.exists(exe_file):
        shutil.copy2(exe_file, os.path.join(source_dir, 'dify_chat_tester.exe'))
        print("已复制可执行文件")
    
    # Copy config template
    config_file = os.path.join(project_dir, '.env.config.example')
    if os.path.exists(config_file):
        shutil.copy2(config_file, os.path.join(source_dir, '.env.config.example'))
        print("已复制配置模板")
    
    # Copy Excel template
    excel_file = os.path.join(project_dir, 'dify_chat_tester_template.xlsx')
    if os.path.exists(excel_file):
        shutil.copy2(excel_file, os.path.join(source_dir, 'dify_chat_tester_template.xlsx'))
        print("已复制 Excel 模板")
    
    # Copy README
    readme_file = os.path.join(project_dir, 'README.md')
    if os.path.exists(readme_file):
        shutil.copy2(readme_file, os.path.join(source_dir, 'README.md'))
        print("已复制 README")
    
    # Copy docs folder
    docs_dir = os.path.join(project_dir, 'docs')
    if os.path.exists(docs_dir):
        shutil.copytree(docs_dir, os.path.join(source_dir, 'docs'), dirs_exist_ok=True)
        print("已复制 docs 文件夹")
    
    # Windows exe can be run directly, no need for run.bat script
    
    # Create ZIP
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
    
    print(f'已创建 {zip_filename}')
    return True

if __name__ == '__main__':
    create_zip()