from digital_land.view_model import JSONQueryHelper


class ViewModelGeoQuery:
    def __init__(self, url_base="https://datasette.digital-land.info/view_model"):
        self.url_base = url_base

    def execute(self, latitude, longitude):
        sql = f"""
                SELECT geography.entity, 
                       geography.entry_date, 
                       geography.name, 
                       geography_geom.type as "dataset", 
                       geography.geography as "curie",
                       geography_geom.geojson_full as "geojson" 
                FROM geography, geography_geom
                WHERE geography_geom.geom IS NOT NULL 
                AND WITHIN(GeomFromText('POINT({longitude} {latitude})'), geom) 
                AND geography_geom.entity = geography.entity

        """
        query_url = JSONQueryHelper.make_url(
            f"{self.url_base}.json", params={"sql": sql}
        )
        return JSONQueryHelper.get(query_url).json()