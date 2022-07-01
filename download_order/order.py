import os
import json
import requests
from requests.auth import HTTPBasicAuth
from pyrfc3339 import generate, parse
from datetime import datetime
import pytz
import pdb
import geopandas as gpd
import fiona
import geojson
import time

def rfc3339(Udate):
	""" Convert input date from user to RFC3339 format which is
	supported format for Planet APIs. 

	Parameters
	----------

	Udate : str
	UTC date from user in format of YY-MM-DD 

	Returns
	-------
	str
	Converted to RFC3339 format
	"""	
	date_dt=datetime.strptime(Udate, "%Y-%m-%d")
	RFC3339_date=generate(date_dt.replace(tzinfo=pytz.utc))
	return(RFC3339_date)


def Check_time_input(gte,lte):
	""" Checks whether Input time is continuous and start date is before
	end date or not 

	Parameters
	----------

	gte : str
	Start date in format of YY-MM-DD


	lte : str
	End date in format of YY-MM-DD 

	Returns
	-------
	Error if time input is not continuous.    
	"""	
	start=rfc3339(gte)
	end=rfc3339(lte)
	if pyrfc3339.parse(start)<=pyrfc3339.parse(end):
		print('Start date has to be before End date')
		exit()

def AOI(AOI_path):
	""" gets path of the AOI and returns geodataframe.
	It also converts Coordination Reference system to EPSG:4326
	to meet planet data API requirements. This function supports
	ESRI Shapefile, Keyhole Markup Language (Kml) and Geojson formats.

	Parameters
	----------

	AOI_path : str
	Path of to the AOI in format of path/to/the/file.shp

	Returns
	-------
	Geopandas geodataframe 
	Converted shapefile/kml/geojson into geodataframe 
	"""	
	if AOI_path[-3:]=='shp':
		AOI_gdf = gpd.read_file(AOI_path)
	if AOI_path[-3:]=='kml':
		gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
		AOI_gdf = AOI_gdf.read_file(AOI_path, driver='KML')
	if AOI_path[-3:]=='json':
		AOI_gdf = gpd.read_file(AOI_path)
	AOI_gdf=AOI_gdf.to_crs("EPSG:4326") 
	return(AOI_gdf)

def Create_Request(AOI_path,gte,lte):
	""" Create request for Planet Data API including AOI and TOI of the
	user, and considering only the products that user has permission to
	download. This function only searchs for ortho_visual product of
	PlanetScope data. 

	Parameters
	----------

	AOI_path : str
	Path of to the AOI in format of path/to/the/file.shp

	gte: str
	start time of the search in RFC3339 format

	lte: str
	End time of the search in RFC3339 format

	Returns
	-------
	dict in json format 
	Created request same as requirements to post in PLANET DATA API  
	"""	
	geojson_geometry = Geojson_geometry(AOI_path)
	geometry_filter = {"type": "GeometryFilter","field_name": "geometry","config": geojson_geometry}
	date_range_filter = {"type": "DateRangeFilter","field_name": "acquired","config": {"gte": gte,"lte": lte}}
	permission_filter={"type":"PermissionFilter","config":["assets.analytic:download"]}
	asset_filter={"type": "AssetFilter","config": ["ortho_visual"]}
	combined_filter = {"type": "AndFilter","config": [geometry_filter, date_range_filter,permission_filter,asset_filter]}
	item_type = "PSScene"
	search_request = {"item_types": [item_type], "filter": combined_filter}
	return(search_request)


def Post_Request(AOI_path,gte,lte,PLANET_API_KEY):
	""" Post request for Planet Data API including AOI and TOI of the
	user.  

	Parameters
	----------

	AOI_path : str
	Path of to the AOI in format of path/to/the/file.shp

	gte: str
	start time of the search in RFC3339 format

	lte: str
	End time of the search in RFC3339 format

	PLANET_API_KEY: str
	a key for authentication of the user 

	Returns
	-------
	json format of the response   
	"""	
	search_result = \
	requests.post(
		'https://api.planet.com/data/v1/quick-search',
		auth=HTTPBasicAuth(PLANET_API_KEY, ''),
		json=Create_Request(AOI_path,gte,lte))
	return(search_result.json())



def Geojson_geometry(AOI_path):
	""" creates geometry for Data API and Order API. If input file is empty, 
	it will raise an error. If it is MultiPolygon, it checks for number of vertices,
	and if it exceeds 500, it will raise error. If submitted AOI has an area less 
	than 1 square meter (Planet requirement), it will raise an error. 

	Parameters
	----------

	AOI_path : str
	Path of to the AOI in format of path/to/the/file.shp

	Returns
	-------
	geojson geometry of the geojson  
	"""	
	AOI_gdf=AOI(AOI_path)
	vertices=len(AOI_gdf)

	if vertices==0:
		print('No feature found. Check submitted area of intrest and try again')
		exit()
	if vertices>1:
		print('MultiPolygon feature detected')
	if vertices>500:
		print('Number of vertices for multipolygon object exceeds 500, reduce vertices and try again')
		exit()

	all_geometries=AOI_gdf.unary_union
	tmp=gpd.GeoSeries([all_geometries]).to_json()
	geojson_geometry=geojson.loads(tmp)['features'][0]['geometry']

	AOI_area_gdf=AOI_gdf.to_crs({'init': 'epsg:3857'})
	AOI_area=AOI_area_gdf['geometry'].area.sum()

	if AOI_area<1:
		print('Submitted AOI area is smaller than 1 square meter, submit larger AOI and try again')
		exit()

	return(geojson_geometry)


def Create_Order(image_ids,AOI_path):
	""" Creates order in json format readable for Order API 

	Parameters
	----------
	AOI_path : str
	Path of to the AOI in format of path/to/the/file.shp

	image_ids : list
	list of images 

	Returns
	-------
	geojson geometry of the geojson  
	"""	
	order_request = {"name":"simple order",\
	"products":[{"item_ids":image_ids,"item_type":"PSScene","product_bundle":"visual"}],\
	"tools":[{"clip":{"aoi":Geojson_geometry(AOI_path)}}]}
	return(order_request)


def Request_to_json(request_name,filename):
	""" saves created request in geojson format in the
	current working directory 

	Parameters
	----------

	request_name : dict
	created dictionary in json format for submitting to Planet APIs

	filename: str
	name desired geojson file 

	Returns
	-------
	geojson file with the filename from input 
	"""	
	with open(filename+'.geojson','w') as f:
		return(geojson.dump(request_name, f))


def Post_Order(image_ids,AOI_path,PLANET_API_KEY):
	""" Post request for Planet Order API for selected image ids as an input.
	It also request to clip images based on the input for AOI.  

	Parameters
	----------

	image_ids : list
	list of image ids 
	
	AOI_path : str
	Path of to the AOI in format of path/to/the/file.shp


	PLANET_API_KEY: str
	a key for authentication of the user 

	Returns
	-------
	json format of the response   
	"""	
	order_result =requests.post(
		'https://api.planet.com/compute/ops/orders/v2',
		auth=HTTPBasicAuth(PLANET_API_KEY, ''),
		json=Create_Order(image_ids,AOI_path))
	return(order_result.json())


def Get_Order(res_order,PLANET_API_KEY):
	""" Submit request to the Order API based on the order response
	from post order. 

	Parameters
	----------

	res_order : dict
	post response from Order API in json format


	PLANET_API_KEY: str
	a key for authentication of the user 

	Returns
	-------
	json format of the response   
	"""	
	URL='https://api.planet.com/compute/ops/orders/v2/{}'.format(res_order['id'])
	get_response=requests.get(URL,auth=HTTPBasicAuth(PLANET_API_KEY, ''))
	return(get_response.json())


def download(get_response,PLANET_API_KEY):
	""" Download images which has success status from getting an order

	Parameters
	----------

	get_response : dict
	Get response from Order API in json format


	PLANET_API_KEY: str
	a key for authentication of the user 

	Returns
	-------
	Nothing. Just downloading images in the  current running folder 
	"""	
	all_ordered_images=get_response['_links']['results']
	for i in range(len(all_ordered_images)):
		if all_ordered_images[i]['delivery']=="success":
			result=requests.get(all_ordered_images[i]['location'],auth=HTTPBasicAuth(PLANET_API_KEY, ''))
			print('download status for order '+all_ordered_images[i]['name']+':')
			print(result)


def OrderState(response):
	""" Checks status of an order based on post response to order API.
	If the status is not successfull waits two minutes. (According to Order API
	documentation, Planet tries to succeed orders less than two minutes, so
	this the purpose of two minutes pause)

	Parameters
	----------

	response : dict
	Post response from Order API in json format

	Returns
	-------
	Nothing. Just shows message in the command line for updating user 
	"""	
	if response['state']=='success':
		print('Order is complete and was successful')
	if response['state']=='queued':
		print('The order is accepted and in the queue to run')
		time.sleep(120)
	if response['state']=='running':
		Print('The order is currently being processed')
		time.sleep(120)