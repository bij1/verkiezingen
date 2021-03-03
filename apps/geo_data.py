# import geopandas
#
# df = geopandas.read_file("yourfile.geojson")
import pandas as pd
import json
with open('stemlokalen2017.geojson') as f:
    data = json.load(f)

df_test = pd.json_normalize(data)

from pandas.io.json import json_normalize
df = json_normalize(data["features"])

coords = 'properties.geometry.coordinates'

df2 = (df[coords].apply(lambda r: [(i[0],i[1]) for i in r[0]])
           .apply(pd.Series).stack()
           .reset_index(level=1).rename(columns={0:coords,"level_1":"point"})
           .join(df.drop(coords,1), how='left')).reset_index(level=0)

df2[['lat','long']] = df2[coords].apply(pd.Series)