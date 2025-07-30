import re
import json
import requests

# كلمات دلالية لموقع نصي
location_keywords = ["قرب", "جنب", "بجانب", "عند", "في"]

# قاعدة بيانات مواقع محلية قابلة للتوسع
known_locations = {
    "الحديقة": {"lat": 33.5183, "lon": 36.3062},
    "المركز": {"lat": 33.5090, "lon": 36.2931},
    "المدرسة": {"lat": 33.5155, "lon": 36.3010},
    "المستشفى": {"lat": 33.5110, "lon": 36.2955},
    "البلدية": {"lat": 33.5070, "lon": 36.2901},
    "المسجد": {"lat": 33.5142, "lon": 36.2977}
}

# (اختياري) مفتاح API لخدمة خرائط خارجية
MAPBOX_TOKEN = "YOUR_MAPBOX_ACCESS_TOKEN"

def extract_location_text(text):
    """استخراج جملة الموقع من الوصف النصي"""
    for keyword in location_keywords:
        match = re.search(rf"{keyword}\s+(\w+)", text)
        if match:
            return match.group(0), match.group(1)  # (مثلًا: "قرب الحديقة", "الحديقة")
    return None, None

def query_mapbox(place_text):
    """استدعاء API لتحويل النص إلى إحداثيات"""
    if not MAPBOX_TOKEN:
        return None

    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{place_text}.json"
    params = {
        "access_token": MAPBOX_TOKEN,
        "limit": 1,
        "language": "ar"
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data["features"]:
            lon, lat = data["features"][0]["center"]
            return {"lat": lat, "lon": lon}
    except:
        pass
    return None

def extract_location(text):
    """الدالة الأساسية لإرجاع معلومات الموقع"""
    if not text or len(text.strip()) < 5:
        return {"location_text": "غير محدد", "coordinates": None}

    location_phrase, place_name = extract_location_text(text)
    coordinates = None

    # أولاً نبحث بالقاعدة المحلية
    if place_name in known_locations:
        coordinates = known_locations[place_name]
    else:
        # إذا مش موجود، نجرب خدمة خارجية
        coordinates = query_mapbox(place_name)

    return {
        "location_text": location_phrase or "غير محدد",
        "coordinates": coordinates
    }
