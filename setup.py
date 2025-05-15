from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nathreader",
    version="0.2.0",
    author="Nath",
    author_email="nath@example.com",
    description="A modern PDF reader application with a clean interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/nathreader",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'PyMuPDF>=1.23.0',
        'Pillow>=10.0.0',
        'customtkinter>=5.2.0'
    ],
    entry_points={
        'console_scripts': [
            'nathreader=nathreader.__main__:main',
        ],
    },
    include_package_data=True,
    python_requires='>=3.8',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
