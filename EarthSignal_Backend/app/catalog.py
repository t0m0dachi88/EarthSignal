VARIABLES = [
    {"id":"air_temperature_c","name":"Near-surface air temperature","units":"°C","source":"NASA GLDAS Noah V2.1","available":True,"description":"Annual air-temperature anomalies and decadal trend slopes."},
    {"id":"surface_temperature_c","name":"Surface skin temperature","units":"°C","source":"NASA GLDAS Noah V2.1","available":True,"description":"Annual surface-temperature anomalies and decadal trend slopes."},
    {"id":"precipitation_mm_month","name":"Precipitation","units":"mm/month (trend feature as supplied)","source":"NASA GLDAS Noah V2.1","available":True,"description":"GLDAS precipitation-derived annual anomaly and trend feature; preserve supplied units and metadata."},
    {"id":"evapotranspiration_mm_month","name":"Evapotranspiration","units":"mm/month (trend feature as supplied)","source":"NASA GLDAS Noah V2.1","available":True,"description":"GLDAS evapotranspiration-derived annual anomaly and trend feature."},
    {"id":"topsoil_water_kg_m2","name":"Topsoil water","units":"kg m⁻²","source":"NASA GLDAS Noah V2.1","available":True,"description":"Topsoil soil-water anomalies and trend feature."},
    {"id":"rootzone_water_kg_m2","name":"Rootzone water","units":"kg m⁻²","source":"NASA GLDAS Noah V2.1","available":True,"description":"Rootzone soil-water anomalies and trend feature."},
]
DATASETS = [
    {"id":"GLDAS_NOAH025_M","name":"GLDAS Noah Land Surface Model L4 Monthly 0.25° V2.1","provider":"NASA GSFC","version":"2.1","period_start":"2003-01","period_end":"2023-12","status":"integrated_assets_available","variables":[v["id"] for v in VARIABLES],"source_url":"https://disc.gsfc.nasa.gov/datasets/GLDAS_NOAH025_M_2.1/summary"},
    {"id":"GPM_3IMERGM","name":"GPM IMERG Monthly V07","provider":"NASA GES DISC","version":"V07","status":"catalog_only_not_ingested","variables":["precipitation"],"source_url":"https://gpm.nasa.gov/data/imerg"},
    {"id":"M2TMNXSLV","name":"MERRA-2 Single-Level Diagnostics Monthly","provider":"NASA GES DISC","version":"MERRA-2","status":"catalog_only_not_ingested","variables":["near-surface air temperature"],"source_url":"https://disc.gsfc.nasa.gov/datasets?keywords=MERRA-2"},
    {"id":"MOD13C2.061","name":"MODIS Vegetation Indices Monthly 0.05°","provider":"NASA LP DAAC","version":"061","status":"catalog_only_not_ingested","variables":["NDVI","EVI"],"source_url":"https://lpdaac.usgs.gov/products/mod13c2v061/"},
]
VARIABLE_BY_ID = {v["id"]: v for v in VARIABLES}
