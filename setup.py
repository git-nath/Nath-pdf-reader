from setuptools import setup, find_packages

setup(
    name="NathFileReader",
    version="1.0.0",
    author="Your Name",
    description="A modern file reader application for Windows 11",
    packages=find_packages(),
    install_requires=[
        'PyMuPDF>=1.19.0',
        'python-docx>=0.8.11',
        'python-pptx>=0.6.21',
        'Pillow>=9.0.0',
        'customtkinter>=5.2.0'
    ],
    entry_points={
        'console_scripts': [
            'nathfilereader=main:main',
        ],
    },
    include_package_data=True,
    python_requires='>=3.7',
)
