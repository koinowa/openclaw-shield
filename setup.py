from setuptools import setup, find_packages

setup(
    name="openclaw-shield",
    version="0.2.0",
    description="Enterprise-grade Security Component for OpenClaw Autonomous AI Agents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/USERNAME/openclaw-shield",
    author="Your Name",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
