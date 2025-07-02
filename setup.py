from setuptools import setup, find_packages
import os
import re

# Read version, author, and email from __init__.py
def get_package_info():
    init_file = os.path.join(os.path.dirname(__file__), 'chroma_memo', '__init__.py')
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M)
    author_match = re.search(r"^__author__ = ['\"]([^'\"]*)['\"]", content, re.M)
    email_match = re.search(r"^__email__ = ['\"]([^'\"]*)['\"]", content, re.M)
    
    if not version_match:
        raise RuntimeError("Unable to find version string.")
    
    return {
        'version': version_match.group(1),
        'author': author_match.group(1) if author_match else "Unknown",
        'email': email_match.group(1) if email_match else "unknown@example.com"
    }

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Get package information
package_info = get_package_info()

setup(
    name="chroma-memo",
    version=package_info['version'],
    author=package_info['author'],
    author_email=package_info['email'],
    description="Project-specific knowledge base using ChromaDB and OpenAI embeddings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/chroma-memo",
    packages=find_packages(),
    package_data={
        'chroma_memo': ['templates/*.md'],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "chroma-memo=chroma_memo.cli:main",
        ],
    },
) 