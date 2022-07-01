import setuptools

with open("README.md", "r", encoding="utf-8") as fhand:
    long_description = fhand.read()

setuptools.setup(
    name="download_order",
    version="0.0.1",
    author="Mehrdad Moshtaghi",
    author_email="mehr.moshtaghi@gmail.com",
    description=("A package for ordering and downloading PlanetScope ortho visual products"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Mehrdad-Moshtaghi/download_order",
    project_urls={
        "Bug Tracker": "https://github.com/Mehrdad-Moshtaghi/download_order/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests","geojson","pyrfc3339","datetime","pytz","geopandas","fiona"],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "download_order = download_order.cli:main",
        ]
    }
)