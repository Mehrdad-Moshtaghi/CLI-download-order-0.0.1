"""
The command-line interface for creating and downloading orders
"""
import argparse
from .order import rfc3339
from .order import Check_time_input
from .order import AOI
from .order import Create_Request
from .order import Post_Request
from .order import Create_Order
from .order import Request_to_json
from .order import Post_Order
from .order import Geojson_geometry
from .order import OrderState
from .order import download
from .order import Online_Readme

def main():
    parser = argparse.ArgumentParser(
        description="A Command Line Interface for downloading orthovisual Planetscope images over your Area of Interest"
    )
    parser.add_argument(
        "Sdate", type=str,
        help="Start date for searching planet images in format of YYYY-MM-DD in UTC time zone"
    )
    parser.add_argument(
        "Edate", type=str,
        help="End date for searching planet images in format of YYYY-MM-DD in UTC time zone"
    )
    parser.add_argument(
        "AOI", type=str,
        help="path to Area of Intrest for searching planet images in format of ESRI shapefile/KML/Geojson\
        for example: Path/to/your/folder/AOI.shp"
    )
    parser.add_argument(
        "PLANET_API_KEY", type=str,
        help="Your planet API key"
    )

    args = parser.parse_args()

    Check_time_input(args.Sdate,args.Edate)
    Result_json=Post_Request(args.AOI,rfc3339(args.Sdate),rfc3339(args.Edate),args.PLANET_API_KEY)
    image_ids = [feature['id'] for feature in Result_json['features']]
    res_order=Post_Order(image_ids,args.AOI,args.PLANET_API_KEY)

    OrderState(res_order)
    if res_order['state']!='success':
        res_order=Post_Order(image_ids,args.AOI,args.PLANET_API_KEY)
        print('Checking Order status...')
        OrderState(res_order)
    if res_order['state']!='success':
        print("Your Order is not ready for download, please try again later")
        exit()

    get_response=Get_Order(res_order,PLANET_API_KEY)
    download(get_response,PLANET_API_KEY)


if __name__ == "__main__":
    main()

