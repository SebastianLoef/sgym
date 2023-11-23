from setuptools import setup, find_packages

setup(
    name="sgym",
    version="0.0.1",
    author="Sebastian Löf",
    description="A gym-like environment for games",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)