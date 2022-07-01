# CLI for ordering and downloading PlanetScope ortho visual products

This tool is for ordering and downloading PlanetScope ortho visual products 


## Installation

Download the zip from this page.
Then you can easily install the module using `pip` from the downloaded zipfile.
```
pip install CLI-download-order-0.0.1-main.zip
```
From GitHub source:
```
git clone https://github.com/Mehrdad-Moshtaghi/CLI-download-order-0.0.1.git
cd CLI-download-order-0.0.1
python setup.py install
```
## Using the CLI command
```
download_order [-h] Sdate Edate AOI PLANET_API_KEY
```
Start is start date for searching planet images in format of YYYY-MM-DD in UTC time zone

Edate is End date for searching planet images in format of YYYY-MM-DD in UTC time zone

AOI is the path to Area of Interest for searching planet images in format of ESRI shapefile/KML/Geojson for example: Path/to/your/folder/AOI.shp

PLANET_API_KEY is your Planet API key

-h help of the CLI tool 


Here is the example of usage:
```
download_order 2020-08-12 2021-09-12 AOI.shp PLANET_API_KEY
```
## Limitations of usage
- CLI tool only downloads products which the user has permission to download.
- geometry of submitted AOI must have area less than 1 square meter, otherwise CLI tool reports an error message.
- Number of vertices for Multipolygon objects has to be less than 500, otherwise the CLI tool reports an error message.
- There is no concern about the Coordination Reference System of the submitted AOI.


## Next steps
Here are the steps which I thoughht it is less important to have, but it is in the context of the CLI tool. If I wanted to spend more time, I would add these things:
- Finding products which is in the submitted user AOI and TOI, but user doesn't have permission to download. 
Then Reporting those product ids to the user in a csv format.  
- Raiseerror function can be added to reduce code length. 
- Paths can be handled much smarter using pathlib library, 
- Checking geometry constraints in more details. As I read AOI in geodataframe, I easily have access to the geometries column, and based on that I can develop functions to do filter AOI based on these steps and raise error:
1) Multipolygon with holes or with multiple exterior rings. 
2) Multipolygon with overlapping/intersecting Polygons
Based on my experience in geospatial domain, the chance of submitting these two cases by a customer is rare, therefore I didn't put it in my first priority list of developments. Although I do agree that the CLI tool must be comprehensive for all cases. 
- General github usage and running of the tool considering different operating systems can be added to readme documentation. 

## Test
There is a test script which generates requests and save them in geojson format in the test_results folder. This is only for validation of developed code based on comparison to the API documentations. There are samples for Data API and Order API next to an example of a multipolygon case. 


## Out of context 
Here I'm summarizing points which are out of context of developing this tool, but it would be useful to add:
- Raising error based on Post responses. Although the CLI tool is supposed to focus on input limitations, this would be interesting to add. From the post response documentation, I see there are already error messages. But I'm not sure if it will be reported in the CLI or not as I don't have access to API keys. 
- There are many more constraints in the documentation which I did not consider as it was not related to input data to the CLI tool. 