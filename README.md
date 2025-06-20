# Dagster Reload Code Location Example

This repo shows an example of how to use a sensor in dagster to reload a code location which uses an asset factory to generate assets from a file. 

The example could be expanded to work with any asset specification source, such as a database table, collection, list of files in a google drive etc. 

The key idea is that we use an asset factory to generate assets from an external source dynamically. 

Then there is a sensor that runs every 30 seconds and checks if that source has been updated, if it has, we use the graphql endpoint to trigger a reload of the code location.

Some opens:
- how does the reload of assets potentially effect the metadata tracking on assets?
- How does this work with 100K assets for example? 