from setuptools import find_packages, setup

setup(
    name="sgym",
    version="0.0.1",
    author="Sebastian Löf",
    description="A gym-like environment for games",
    packages=["sgym", "sgym.games", "sgym.games._2048"],
    install_requires=[
        "pygame",
        "numpy",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
