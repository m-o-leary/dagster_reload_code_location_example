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

# Sensor that can trigger asset materializations on a cadence
@dg.sensor(
    asset_selection=dg.AssetSelection.assets(*[asset.key for asset in generated_assets]),
    minimum_interval_seconds=300  # 5 minutes
)
def factory_assets_sensor(context: dg.SensorEvaluationContext):
    # Logic to determine when to materialize assets
    # This runs every 5 minutes and can trigger asset materializations
    
    should_run = True  # Your condition logic here
    
    if should_run:
        # Materialize all factory-generated assets
        yield dg.RunRequest(
            asset_selection=[asset.key for asset in generated_assets]
        )
    else:
        yield dg.SkipReason("Conditions not met for asset materialization")

defs = dg.Definitions(
    assets=generated_assets,
    sensors=[json_file_reload_sensor],
)