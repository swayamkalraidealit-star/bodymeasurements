"""Test size recommendation logic"""
import json
from app.services.size_recommender import SizeRecommender
from app.models.garment_specs import GarmentCategory

# Initialize recommender
recommender = SizeRecommender()

# Test measurements - typical measurements for different sizes
test_cases = [
    {
        "name": "Small person (should get XS/S)",
        "measurements": {
            "chest": 88,
            "waist": 78,
            "shoulder_width": 43,
            "height": 168
        },
        "category": GarmentCategory.MENS_SHIRT
    },
    {
        "name": "Medium person (should get M)",
        "measurements": {
            "chest": 97,
            "waist": 86,
            "shoulder_width": 46,
            "height": 175
        },
        "category": GarmentCategory.MENS_SHIRT
    },
    {
        "name": "Large person (should get L/XL)",
        "measurements": {
            "chest": 104,
            "waist": 93,
            "shoulder_width": 49,
            "height": 180
        },
        "category": GarmentCategory.MENS_SHIRT
    },
    {
        "name": "Woman Medium (should get M)",
        "measurements": {
            "chest": 91,
            "waist": 73,
            "hip": 98,
            "shoulder_width": 41,
            "height": 170
        },
        "category": GarmentCategory.WOMENS_TOP
    }
]

print("=" * 80)
print("SIZE RECOMMENDATION LOGIC TEST")
print("=" * 80)

for test in test_cases:
    print(f"\n{test['name']}")
    print(f"Measurements: {test['measurements']}")
    print(f"Category: {test['category'].value}")
    print("-" * 80)
    
    recommendations = recommender.recommend_sizes(
        user_measurements=test['measurements'],
        category=test['category'],
        top_n=5
    )
    
    print(f"\nTop {len(recommendations)} Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. Size: {rec.size}")
        print(f"   Fit Score: {rec.fit_score}/100")
        print(f"   Fit Category: {recommender.get_fit_category(rec.fit_score)}")
        print(f"   Garment Measurements: {json.dumps(rec.measurements, indent=6)}")
        print(f"   Fit Analysis:")
        for key, value in rec.fit_analysis.items():
            print(f"     - {key}: {value}")
    
    print("\n" + "=" * 80)

# Now test the edge case - someone exactly matching a size
print("\n\nEDGE CASE: Exact Match Test")
print("=" * 80)
exact_match_test = {
    "name": "Exact M size match",
    "measurements": {
        "chest": 97,  # Exact M
        "waist": 86,  # Exact M
        "shoulder_width": 46,  # Exact M
        "height": 175  # Middle of M range (170-180)
    },
    "category": GarmentCategory.MENS_SHIRT
}

print(f"{exact_match_test['name']}")
print(f"Measurements: {exact_match_test['measurements']}")
recommendations = recommender.recommend_sizes(
    user_measurements=exact_match_test['measurements'],
    category=exact_match_test['category'],
    top_n=5
)

for i, rec in enumerate(recommendations, 1):
    print(f"\n{i}. Size: {rec.size} - Score: {rec.fit_score}/100")
    print(f"   Category: {recommender.get_fit_category(rec.fit_score)}")

print("\n" + "=" * 80)
