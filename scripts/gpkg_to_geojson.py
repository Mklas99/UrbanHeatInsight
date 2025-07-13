import argparse
import os
# import json (removed as it is not used)
from osgeo import ogr


def convert_gpkg_to_geojson(gpkg_path: str, output_path: str, layer_name: str = None):
    # Open the GeoPackage
    driver = ogr.GetDriverByName("GPKG")
    data_source = driver.Open(gpkg_path, 0)  # 0 = read-only

    if data_source is None:
        raise RuntimeError(f"Cannot open file: {gpkg_path}")

    # List all layers if no layer specified
    if layer_name is None:
        layer = data_source.GetLayer(0)
        layer_name = layer.GetName()
        print(f"No layer name provided. Using first layer: '{layer_name}'")
    else:
        layer = data_source.GetLayerByName(layer_name)

    if not layer:
        raise RuntimeError(f"Layer '{layer_name}' not found in {gpkg_path}")

    # Convert to GeoJSON
    geojson_driver = ogr.GetDriverByName("GeoJSON")
    if os.path.exists(output_path):
        geojson_driver.DeleteDataSource(output_path)

    geojson_ds = geojson_driver.CreateDataSource(output_path)
    geojson_ds.CopyLayer(layer, layer.GetName())
    geojson_ds = None  # Close and flush

    print(f"✅ Layer '{layer_name}' exported to '{output_path}'")


def list_layers(gpkg_path: str):
    driver = ogr.GetDriverByName("GPKG")
    ds = driver.Open(gpkg_path, 0)
    if not ds:
        raise RuntimeError(f"Could not open {gpkg_path}")

    print("Available layers:")
    for i in range(ds.GetLayerCount()):
        layer = ds.GetLayer(i)
        print(f" - {layer.GetName()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert GPKG to GeoJSON using GDAL")
    parser.add_argument("input", help="Input .gpkg file")
    parser.add_argument("-o", "--output", help="Output .geojson file (default: input_basename.geojson)")
    parser.add_argument("-l", "--layer", help="Layer name to convert (default: first layer)")
    parser.add_argument("--list", action="store_true", help="List available layers only")

    args = parser.parse_args()

    if args.list:
        list_layers(args.input)
    else:
        out_file = args.output or os.path.splitext(args.input)[0] + ".geojson"
        convert_gpkg_to_geojson(args.input, out_file, args.layer)

# Example usage:
# python gpkg_to_geojson.py input.gpkg -o output.geojson -l layer_name
# python gpkg_to_geojson.py ../downloaded_data/FMZK_WIEN_20250101_GP/FMZK_WIEN_20250101_GP.gpkg --list
