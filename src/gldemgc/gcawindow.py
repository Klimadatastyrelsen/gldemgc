import argparse
from osgeo import gdal, osr
import sys

gdal.UseExceptions()
osr.UseExceptions()

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('dem', type=str, help='path to DEM raster')
    parser.add_argument('gca', type=str, help='path to GCA raster')
    parser.add_argument('warped_dem', type=str, help='desired path to warped output DEM (COG)')
    parsed_args = parser.parse_args(args)
    return parsed_args

def main():
    input_args = parse_args(sys.argv[1:])

    input_dem_path = input_args.dem
    input_gca_path = input_args.gca
    output_dem_path = input_args.warped_dem

    gca_dataset = gdal.Open(input_gca_path)
    gca_srs = gca_dataset.GetSpatialRef()
    gca_extent = gca_dataset.GetExtent()

    # Note different order in GetExtent() and TranslateOptions' projWin
    x_min, x_max, y_min, y_max = gca_extent
    proj_win = (x_min, y_max, x_max, y_min)

    translate_options = gdal.TranslateOptions(
        format='COG',
        projWin=proj_win,
        projWinSRS=gca_srs
    )

    gdal.Translate(output_dem_path, input_dem_path, options=translate_options)
