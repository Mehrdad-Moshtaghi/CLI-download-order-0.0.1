from order import *
import pdb

#sample request to DataAPI 
AOI_path='../sample_shapefile/sample_shapefile.shp'
tmp=Create_Request(AOI_path,rfc3339('2020-08-01'),rfc3339('2021-09-12'))
Request_to_json(tmp,'../test_results/sample_request_DataAPI')

#sample request to OrderAPI 
image_ids=["20200922_183724_23_106a","20200922_183722_17_106a"]
tmp=Create_Order(image_ids,AOI_path)
Request_to_json(tmp,'../test_results/sample_request_OrderAPI')

#sample request to DataAPI with multipolygon
AOI_path='../sample_shapefile/MultiPolygon_sample.shp'
tmp=Create_Request(AOI_path,rfc3339('2020-08-01'),rfc3339('2021-09-12'))
Request_to_json(tmp,'../test_results/sample_request_DataAPI_MultiPolygon')