"""Comprehensive visual test of size recommendation improvements"""
from app.services.size_recommender import SizeRecommender
from app.models.garment_specs import GarmentCategory

recommender = SizeRecommender()

print("=" * 80)
print("SIZE RECOMMENDATION SYSTEM - COMPREHENSIVE VERIFICATION")
print("=" * 80)

# Test various edge cases
test_cases = [
    {
        "name": "Borderline XS/S (closer to XS)",
        "measurements": {"chest": 87, "waist": 77, "shoulder_width": 42, "height": 167},
        "category": GarmentCategory.MENS_SHIRT,
        "expected_first": "XS"
    },
    {
        "name": "Borderline S/M (closer to S)",  
        "measurements": {"chest": 93, "waist": 83, "shoulder_width": 45, "height": 172},
        "category": GarmentCategory.MENS_SHIRT,
        "expected_first": "S"
    },
    {
        "name": "Borderline M/L (closer to M)",
        "measurements": {"chest": 99, "waist": 88, "shoulder_width": 47, "height": 177},
        "category": GarmentCategory.MENS_SHIRT,
        "expected_first": "M"
    },
    {
        "name": "Exact M match",
        "measurements": {"chest": 97, "waist": 86, "shoulder_width": 46, "height": 175},
        "category": GarmentCategory.MENS_SHIRT,
        "expected_first": "M"
    },
    {
        "name": "Between L and XL (closer to L)",
        "measurements": {"chest": 104, "waist": 93, "shoulder_width": 49, "height": 180},
        "category": GarmentCategory.MENS_SHIRT,
        "expected_first": "L"
    }
]

passed = 0
failed = 0

for test in test_cases:
    print(f"\n{'─' * 80}")
    print(f"Test: {test['name']}")
    print(f"Measurements: {test['measurements']}")
    print(f"Expected first recommendation: {test['expected_first']}")
    
    recommendations = recommender.recommend_sizes(
        user_measurements=test['measurements'],
        category=test['category'],
        top_n=3
    )
    
    actual_first = recommendations[0].size if recommendations else None
    
    print(f"\nTop 3 Recommendations:")
    for i, rec in enumerate(recommendations[:3], 1):
        marker = "✓" if i == 1 and rec.size == test['expected_first'] else " "
        print(f"  {marker} {i}. {rec.size}: {rec.fit_score:.1f}/100 - {recommender.get_fit_category(rec.fit_score)}")
        for key, value in rec.fit_analysis.items():
            print(f"      • {key}: {value}")
    
    # Verify
    if actual_first == test['expected_first']:
        print(f"\n✅ PASS: Got expected size '{test['expected_first']}'")
        passed += 1
    else:
        print(f"\n❌ FAIL: Expected '{test['expected_first']}' but got '{actual_first}'")
        failed += 1

print(f"\n{'=' * 80}")
print(f"TEST SUMMARY")
print(f"{'=' * 80}")
print(f"✅ Passed: {passed}/{len(test_cases)}")
print(f"❌ Failed: {failed}/{len(test_cases)}")

if failed == 0:
    print(f"\n🎉 ALL TESTS PASSED! Size recommendation logic is working correctly!")
else:
    print(f"\n⚠️  {failed} test(s) failed. Review the logic.")

print("=" * 80)
