import json
import dagster as dg
import pathlib  
from lib.sensors import json_file_reload_sensor
# Asset factory function
def create_data_asset(name: str, source_table: str):
    @dg.asset(name=name)
    def _asset(context: dg.AssetExecutionContext):
        context.log.info(f"Processing {source_table}")
        # Your data processing logic here
        return f"Data from {source_table}"
    
    return _asset

# Generate assets using the factory
asset_configs = json.load((pathlib.Path(__file__).parent / "assets.json").resolve().open())  # noqa: F821

generated_assets = [
    create_data_asset(config["name"], config["source_table"]) 
    for config in asset_configs
]

defs = dg.Definitions(
    assets=generated_assets,
    sensors=[json_file_reload_sensor],
)