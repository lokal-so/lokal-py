from setuptools import setup, find_packages

setup(
    name="lokal-py",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "colorama>=0.4.6",
        "packaging>=20.9",
    ],
    author="RUBI JIHANTORO",
    author_email="ceo@lokal.so",
    description="A Python client for interacting with Lokal Client REST API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/lokal-so/lokal-py",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
