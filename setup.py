from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ast_ari_py",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A high-performance Python library for Asterisk REST Interface (ARI)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ast_ari_py",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        "aiohttp>=3.8.0",
        "ujson>=5.0.0",
        "yarl>=1.7.0",
    ],
)
