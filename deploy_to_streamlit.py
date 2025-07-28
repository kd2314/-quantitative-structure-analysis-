#!/usr/bin/env python3
"""
Streamlit Cloud 部署助手
这个脚本帮助你将应用部署到Streamlit Cloud
"""

import os
import subprocess
import sys

def check_git_installed():
    """检查Git是否已安装"""
    try:
        subprocess.run(['git', '--version'], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def init_git_repo():
    """初始化Git仓库"""
    if not check_git_installed():
        print("❌ Git未安装，请先安装Git")
        print("下载地址: https://git-scm.com/downloads")
        return False
    
    try:
        # 检查是否已经是Git仓库
        if os.path.exists('.git'):
            print("✅ Git仓库已存在")
            return True
        
        # 初始化Git仓库
        subprocess.run(['git', 'init'], check=True)
        print("✅ Git仓库初始化成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git仓库初始化失败: {e}")
        return False

def create_gitignore():
    """创建.gitignore文件"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Streamlit
.streamlit/secrets.toml

# Generated files
*.png
*.xlsx
*.csv
stock_*_macd_*.png
stock_*_macd_*.xlsx
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    print("✅ .gitignore文件创建成功")

def check_required_files():
    """检查必需文件是否存在"""
    required_files = [
        'streamlit_app.py',
        'judge_strategy.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必需文件: {', '.join(missing_files)}")
        return False
    
    print("✅ 所有必需文件都存在")
    return True

def main():
    print("🚀 Streamlit Cloud 部署助手")
    print("=" * 50)
    
    # 检查必需文件
    if not check_required_files():
        return
    
    # 创建.gitignore
    create_gitignore()
    
    # 初始化Git仓库
    if not init_git_repo():
        return
    
    print("\n📋 下一步操作:")
    print("1. 在GitHub上创建新仓库")
    print("2. 运行以下命令上传代码:")
    print("   git add .")
    print("   git commit -m 'Initial commit'")
    print("   git branch -M main")
    print("   git remote add origin https://github.com/你的用户名/仓库名.git")
    print("   git push -u origin main")
    print("\n3. 访问 https://share.streamlit.io/ 部署应用")
    print("4. 选择你的GitHub仓库和streamlit_app.py文件")
    
    print("\n📖 详细说明请查看: 部署到Streamlit_Cloud.md")

if __name__ == "__main__":
    main() 