from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name='screen-translator',
    version='1.0.0',
    author='Screen Translator Team',
    author_email='contact@screentranslator.com',
    description='แอปพลิเคชัน Windows สำหรับแปลข้อความบนหน้าจอแบบ real-time',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/screen-translator",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics :: Capture :: Screen Capture",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'screen-translator=main:main',
        ],
    },
    keywords=[
        "ocr", "translation", "screen-capture", "real-time", 
        "tesseract", "google-translate", "pyqt5", "gui"
    ],
    project_urls={
        "Bug Reports": "https://github.com/yourusername/screen-translator/issues",
        "Source": "https://github.com/yourusername/screen-translator",
        "Documentation": "https://github.com/yourusername/screen-translator/wiki",
    },
)
        ],
    },
)