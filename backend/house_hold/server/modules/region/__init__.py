from .region import RegionCityQuery, RegionProvinceQuery


urls = [
    ("/api/region_province/query", RegionProvinceQuery),
    ("/api/region_city/query", RegionCityQuery)
]