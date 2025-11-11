from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="okin-bed-control",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Python library for controlling OKIN adjustable beds via Bluetooth LE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/okin-bed-control",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Home Automation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "bleak>=0.20.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.20.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
        "server": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "pydantic>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "okin-bed=okin_bed.cli:main",
            "okin-bed-server=okin_bed.api_server:main",
        ],
    },
)
