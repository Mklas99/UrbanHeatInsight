from osgeo import ogr
import json
import tempfile
import os


class GPKGtoGeoJSONConverter:
    def __init__(self, gpkg_path: str):
        self.gpkg_path = gpkg_path

    def convert(self, layer_name: str = None) -> dict:
        """
        Converts the specified layer of a GPKG file to GeoJSON.

        :param layer_name: Optional name of the layer. If None, uses the first one.
        :return: GeoJSON as a Python dict.
        """
        driver = ogr.GetDriverByName("GPKG")
        data_source = driver.Open(self.gpkg_path, 0)  # 0 = read-only
        if data_source is None:
            raise RuntimeError(f"Cannot open file: {self.gpkg_path}")

        if layer_name:
            layer = data_source.GetLayerByName(layer_name)
        else:
            layer = data_source.GetLayer(0)  # first layer

        if not layer:
            raise RuntimeError("Could not access the specified layer.")

        # Convert layer to GeoJSON
        geojson_driver = ogr.GetDriverByName("GeoJSON")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".geojson") as tmpfile:
            geojson_path = tmpfile.name

        geojson_ds = geojson_driver.CreateDataSource(geojson_path)
        geojson_layer = geojson_ds.CopyLayer(layer, layer.GetName())
        geojson_ds = None  # Close to flush to disk

        with open(geojson_path, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)

        os.remove(geojson_path)
        return geojson_data
