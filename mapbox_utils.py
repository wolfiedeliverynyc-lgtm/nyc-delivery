"""
mapbox_utils.py - Mapbox أدوات
Geocoding, Directions, Static Maps, Navigation
"""

import requests
from typing import Optional, Dict, Tuple
from geopy.distance import geodesic
import logging

log = logging.getLogger(__name__)


class MapboxUtils:
    """Mapbox API utilities"""
    
    GEOCODING_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"
    DIRECTIONS_URL = "https://api.mapbox.com/directions/v5/mapbox/driving"
    STATIC_MAP_URL = "https://api.mapbox.com/styles/v1/mapbox/dark-v11/static"
    
    def __init__(self, access_token: str):
        self.token = access_token
    
    def geocode(self, address: str, proximity: Optional[Tuple] = None) -> Optional[Dict]:
        """
        تحويل العنوان إلى إحداثيات
        
        Args:
            address: العنوان النصي
            proximity: إحداثيات قريبة للبحث حولها (lat, lon)
        
        Returns:
            {"lat": float, "lon": float, "address": str} أو None
        """
        try:
            url = f"{self.GEOCODING_URL}/{requests.utils.quote(address)}.json"
            
            params = {
                "access_token": self.token,
                "limit": 1,
                "country": "US",
                "types": "address,poi"
            }
            
            if proximity:
                params["proximity"] = f"{proximity[1]},{proximity[0]}"
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            features = response.json().get("features", [])
            
            if features:
                coords = features[0]["geometry"]["coordinates"]
                return {
                    "lat": coords[1],
                    "lon": coords[0],
                    "address": features[0].get("place_name", address)
                }
        
        except Exception as e:
            log.error(f"Geocoding error for '{address}': {e}")
        
        return None
    
    def get_directions(self, origin: Tuple, destination: Tuple) -> Optional[Dict]:
        """
        الحصول على المسار بين نقطتين
        
        Args:
            origin: (lat, lon)
            destination: (lat, lon)
        
        Returns:
            {"km": float, "min": float} أو None
        """
        try:
            # Mapbox uses lon,lat format
            coords = f"{origin[1]},{origin[0]};{destination[1]},{destination[0]}"
            
            params = {
                "access_token": self.token,
                "geometries": "geojson",
                "overview": "full"
            }
            
            response = requests.get(
                f"{self.DIRECTIONS_URL}/{coords}.json",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            routes = response.json().get("routes", [])
            
            if routes:
                route = routes[0]
                return {
                    "km": round(route["distance"] / 1000, 2),
                    "min": round(route["duration"] / 60, 1)
                }
        
        except Exception as e:
            log.error(f"Directions error: {e}")
        
        return None
    
    def get_static_map_url(self, point_a: Tuple, point_b: Tuple, 
                          width: int = 800, height: int = 400) -> str:
        """
        الحصول على رابط خريطة ثابتة
        
        Args:
            point_a: (lat, lon) - المطعم
            point_b: (lat, lon) - الزبون
            width: عرض الصورة
            height: ارتفاع الصورة
        
        Returns:
            URL للخريطة
        """
        # Markers: A (restaurant - red), B (customer - green)
        markers = (
            f"pin-s-a+f44336({point_a[1]},{point_a[0]}),"
            f"pin-s-b+4caf50({point_b[1]},{point_b[0]})"
        )
        
        return (
            f"{self.STATIC_MAP_URL}/{markers}/"
            f"auto/{width}x{height}@2x"
            f"?access_token={self.token}"
        )
    
    @staticmethod
    def get_navigation_url(origin: Tuple, destination: Tuple) -> str:
        """
        الحصول على رابط Google Maps للملاحة
        
        Args:
            origin: (lat, lon)
            destination: (lat, lon)
        
        Returns:
            Google Maps URL
        """
        return (
            f"https://www.google.com/maps/dir/?api=1"
            f"&origin={origin[0]},{origin[1]}"
            f"&destination={destination[0]},{destination[1]}"
            f"&travelmode=driving"
        )
    
    @staticmethod
    def calculate_distance(point_a: Tuple, point_b: Tuple) -> float:
        """
        حساب المسافة بين نقطتين (fallback)
        
        Args:
            point_a: (lat, lon)
            point_b: (lat, lon)
        
        Returns:
            المسافة بالكيلومترات
        """
        try:
            return round(geodesic(point_a, point_b).km, 2)
        except:
            return 0.0
