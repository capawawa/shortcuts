from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="shortcuts-doc-generator",
    version="1.0.0",
    description="A comprehensive documentation generator for Apple Shortcuts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/capawawa/shortcuts",
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "rich>=10.0.0",
        "networkx>=2.6.0",
        "matplotlib>=3.4.0",
        "jinja2>=3.0.0",
        "pyyaml>=5.4.0",
        "markdown>=3.3.0"
    ],
    entry_points={
        "console_scripts": [
            "shortcuts-doc=cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
        "Topic :: Utilities",
    ],
    keywords="apple shortcuts documentation generator analyzer",
    project_urls={
        "Bug Reports": "https://github.com/capawawa/shortcuts/issues",
        "Source": "https://github.com/capawawa/shortcuts",
    },
    package_data={
        "shortcuts_doc_generator": [
            "templates/*.md",
            "templates/*.html",
            "config/*.yaml",
        ],
    },
) 