"""Garment specification models."""
from enum import Enum
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
import json
import os


class GarmentCategory(str, Enum):
    """Garment category types."""
    MENS_SHIRT = "MENS_SHIRT"
    WOMENS_TOP = "WOMENS_TOP"
    MENS_PANTS = "MENS_PANTS"
    WOMENS_PANTS = "WOMENS_PANTS"
    DRESS = "DRESS"


class SizeSpecification(BaseModel):
    """Measurements for a specific size."""
    chest: Optional[float] = Field(None, description="Chest circumference in cm")
    waist: Optional[float] = Field(None, description="Waist circumference in cm")
    hip: Optional[float] = Field(None, description="Hip circumference in cm")
    shoulder_width: Optional[float] = Field(None, description="Shoulder width in cm")
    inseam: Optional[float] = Field(None, description="Inseam length in cm")
    height_range: Optional[Tuple[int, int]] = Field(None, description="Recommended height range in cm")


class SizeChart(BaseModel):
    """Size chart for a garment category."""
    name: str = Field(..., description="Human-readable garment name")
    sizes: Dict[str, SizeSpecification] = Field(..., description="Size specifications by size name")


class SizeChartDatabase:
    """Database of standard size charts."""
    
    _instance = None
    _size_charts: Dict[GarmentCategory, SizeChart] = {}
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(SizeChartDatabase, cls).__new__(cls)
            cls._instance._load_size_charts()
        return cls._instance
    
    def _load_size_charts(self):
        """Load size charts from JSON file."""
        # Get the path to size_charts.json
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, '..', 'data', 'size_charts.json')
        
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Parse JSON into SizeChart objects
            for category_key, category_data in data.items():
                category = GarmentCategory(category_key)
                
                sizes = {}
                for size_name, size_data in category_data['sizes'].items():
                    sizes[size_name] = SizeSpecification(**size_data)
                
                self._size_charts[category] = SizeChart(
                    name=category_data['name'],
                    sizes=sizes
                )
                
        except Exception as e:
            print(f"Error loading size charts: {e}")
            # Load default empty charts
            self._size_charts = {}
    
    def get_size_chart(self, category: GarmentCategory) -> Optional[SizeChart]:
        """Get size chart for a specific category."""
        return self._size_charts.get(category)
    
    def get_all_categories(self) -> List[Dict[str, str]]:
        """Get list of all available categories."""
        return [
            {
                "key": category.value,
                "name": chart.name
            }
            for category, chart in self._size_charts.items()
        ]
