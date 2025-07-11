"""
Setup script for Smart Home Expense & Maintenance Analyst Agent
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="smart-home-agent",
    version="1.0.0",
    author="Smart Home Agent Team",
    author_email="contact@smarthomeagent.com",
    description="An intelligent agent for managing household expenses and maintenance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/smart-home-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: FastAPI",
        "Topic :: Office/Business :: Financial",
        "Topic :: Home Automation",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "black>=23.11.0",
            "isort>=5.12.0",
            "mypy>=1.7.1",
            "flake8>=6.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "smart-home-agent=main:app",
        ],
    },
    include_package_data=True,
    package_data={
        "smart_home_agent": ["*.py"],
    },
)
