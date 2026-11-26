# gldemgc
GCP and GCA utility for Greenland DEM

## Installation
To use the software, ensure you have [Pixi](https://pixi.prefix.dev/)
installed. Pixi will take care of ensuring an appropriate environment on first
run.

## Usage
### GCP check
The utility `gcpcheck` will find the discrepancies between a provided DEM
raster and a collection of ground control points (GCPs), optionally with a
user-provided geoid undulation applied. It outputs a GeoPackage (GPKG) file
containing results for each GCP.

```
usage: pixi run gcpcheck [-h] [--geoid GEOID] [--gcp-z-field GCP_Z_FIELD]
                         [--gcp-attribute-filter GCP_ATTRIBUTE_FILTER]
                         [--progress]
                         [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                         dem gcps output

positional arguments:
  dem                   path to DEM raster
  gcps                  path to GCP data
  output                desired path to output (GPKG)

options:
  -h, --help            show this help message and exit
  --geoid GEOID         path to geoid raster
  --gcp-z-field GCP_Z_FIELD
                        name of Z field in GCP features
  --gcp-attribute-filter GCP_ATTRIBUTE_FILTER
                        SQL WHERE-style attribute filter for GCPs
  --progress            show progress bar during processing
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        logging level
```

The `--geoid` argument is optional. If not provided, the program will behave
as if the geoid undulation is zero everywhere.

The Z value for each GCP is extracted from the field specified with
`--gcp-z-field`. If not provided, the program will try to use the geometry Z
of the GCPs.

Note that `--gcp-attribute-filter` arguments may need careful escaping. For
example, to apply `source = "foo"` on Windows CMD, use
`--gcp-attribute-filter "source = \"foo\""`.

The output file will contain 2D points in the same SRS as the GCP input. Each
point will have the following fields:

| Field     | Description |
| --------- | ----------- |
| `dem_z`   | Z value of the raster DEM, point-sampled at the GCP location (using bilinear interpolation) |
| `geoid_z` | Z value of the geoid raster, point-sampled at the GCP location (using bilinear interpolation) |
| `gcp_z`   | GCP Z value |
| `z_diff`  | Difference between DEM and GCP (`dem_z` - (`gcp_z` - `geoid_z`)) |

The following example takes the file `dem.vrt` as the input DEM to check. For
its GCP database, it uses the file `gcps.gpkg`, which is filtered by
`source = "myfriends"`, and their Z value is taken from the field `height`.
The geoidal undulation to use is provided in geoid.tif. Output is written to
the file `results.gpkg`:
```
pixi run gcpcheck dem.vrt gcps.gpkg results.gpkg --geoid geoid.tif --gcp-z-field height --gcp-attribute-filter "source = \"myfriends\""
```

### GCA check (experimental)
The heavy lifting of GCA checks is done by the
[demcoreg](https://github.com/dshean/demcoreg) toolkit developed by David
Shean. For convenience, this project provides a utility for DEM preprocessing
and easy installation of demcoreg.

demcoreg works on materialized rasters, meaning that huge DEMs will not fit in
memory for the analysis. Therefore, a preprocessing utility called `gcawindow`
can extract a window of the DEM covering the GCA. The following command will
read a (possibly large-scale) DEM at `dem.vrt`, read the extent of the GCA in
`gca.tif`, and write the windowed part of the DEM to `windowed_dem.tif`:
```
pixi run gcawindow dem.vrt gca.tif windowed_dem.tif
```

This windowed DEM can now be passed to demcoreg. This project exposes
demcoreg's `dem_align` tool as a Pixi task:
```
pixi run dem_align gca.tif windowed_dem.tif
```
The above command will try to align the raster in `windowed_dem.tif`, using
`gca.tif` as reference. Refer to demcoreg's documentation (and `dem_align`'s
help, with the `-h` argument) for further details.

`dem_align` seems to be problematic on Windows due to
[demcoreg#45](https://github.com/dshean/demcoreg/issues/45).
