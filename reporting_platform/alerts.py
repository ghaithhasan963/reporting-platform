from math import radians, cos, sin, asin, sqrt

def is_nearby(lat1, lon1, lat2, lon2, radius_km=2.0):
    # دالة لحساب المسافة بين نقطتين
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    return 6371 * c <= radius_km  # مسافة الأرض بالكيلومتر
