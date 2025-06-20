import pathlib
import dagster as dg
import os

import requests

def reload_code_location(host: str, port: int, location_name: str) -> dict:
    """
    Sends a GraphQL mutation to reload the specified code location.
    """
    graphql_mutation = """
    mutation ReloadRepositoryLocationMutation($location: String!) {
      reloadRepositoryLocation(repositoryLocationName: $location) {
        ... on WorkspaceLocationEntry {
          id
          loadStatus
          locationOrLoadError {
            ... on RepositoryLocation {
              id
              __typename
            }
            ... on PythonError {
              message
              stack
            }
            __typename
          }
          __typename
        }
        ... on UnauthorizedError {
          message
          __typename
        }
        ... on ReloadNotSupported {
          message
          __typename
        }
        ... on RepositoryLocationNotFound {
          message
          __typename
        }
        ... on PythonError {
          message
          stack
        }
        __typename
      }
    }
    """
    
    variables = {"location": location_name}
    url = f"http://{host}:{port}/graphql"
    
    response = requests.post(
        url,
        json={"query": graphql_mutation, "variables": variables},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        if "errors" in result:
            raise Exception(f"GraphQL errors: {result['errors']}")
        return result
    else:
        raise Exception(f"HTTP error: {response.status_code} - {response.text}")


@dg.sensor(minimum_interval_seconds=30)
def json_file_reload_sensor(context: dg.SensorEvaluationContext):
    # Path to your JSON file
    json_file_path = (pathlib.Path(__file__).parent.parent / "assets.json")
    
    if not os.path.exists(json_file_path):
        return dg.SkipReason("JSON file not found")
    
    # Get current file modification time
    current_mtime = os.path.getmtime(json_file_path)
    
    # Get last processed modification time from cursor
    last_mtime = float(context.cursor) if context.cursor else 0
    
    # Check if file has been modified
    if current_mtime > last_mtime:
        # File has changed, reload the code location
        try:
            reload_code_location(
                host="localhost",  # Your Dagster webserver host
                port=3000,         # Your Dagster webserver port  
                location_name="definitions.py"
            )
            
            # Update cursor with new modification time
            context.update_cursor(str(current_mtime))
            
            return dg.SkipReason(f"JSON file changed, code location reloaded at {current_mtime}")
            
        except Exception as e:
            context.log.error(f"Failed to reload code location: {e}")
            return dg.SkipReason(f"Failed to reload code location: {e}")
    
    return dg.SkipReason("No changes detected in JSON file")
