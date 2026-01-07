"""Debug exact scoring logic"""
from app.services.size_recommender import SizeRecommender
from app.models.garment_specs import GarmentCategory, SizeChartDatabase

# Initialize
recommender = SizeRecommender()
db = SizeChartDatabase()

# Test case
measurements = {
    "chest": 88,
    "waist": 78,
    "shoulder_width": 43,
    "height": 168
}

size_chart = db.get_size_chart(GarmentCategory.MENS_SHIRT)

print("DETAILED SCORING BREAKDOWN")
print("=" * 80)
print(f"User measurements: {measurements}\n")

for size_name, size_spec in size_chart.sizes.items():
    print(f"\n{size_name}:")
    print(f"  Garment: chest={size_spec.chest}, waist={size_spec.waist}, "
          f"shoulder_width={size_spec.shoulder_width}, height_range={size_spec.height_range}")
    
    fit_score, fit_analysis = recommender._calculate_fit_score(measurements, size_spec)
    
    print(f"  TOTAL FIT SCORE: {fit_score}/100")
    print(f"  Analysis: {fit_analysis}")
    
    # Manual calculation
    print(f"\n  Manual breakdown:")
    for measure, user_val in measurements.items():
        if measure == 'height' and size_spec.height_range:
            min_h, max_h = size_spec.height_range
            print(f"    {measure}: user={user_val}, range=[{min_h}, {max_h}]", end="")
            if min_h <= user_val <= max_h:
                print(f" -> IN RANGE (score=100)")
            else:
                if user_val < min_h:
                    diff = min_h - user_val
                    score = max(0, 100 - (diff / recommender.tolerance['height']) * 50)
                else:
                    diff = user_val - max_h
                    score = max(0, 100 - (diff / recommender.tolerance['height']) * 50)
                print(f" -> OUT OF RANGE by {diff}cm (score={score})")
        else:
            garment_val = getattr(size_spec, measure, None)
            if garment_val:
                diff = abs(user_val - garment_val)
                tolerance = recommender.tolerance.get(measure, 3)
                print(f"    {measure}: user={user_val}, garment={garment_val}, diff={diff}cm, tolerance={tolerance}cm", end="")
                if diff <= tolerance:
                    print(f" -> WITHIN TOLERANCE (score=100, weight={recommender.weights.get(measure, 0)})")
                else:
                    excess = diff - tolerance
                    score = max(0, 100 - (excess / tolerance) * 50)
                    print(f" -> OUTSIDE TOLERANCE (score={score}, weight={recommender.weights.get(measure, 0)})")

print("\n" + "=" * 80)
print("\nCONCLUSION:")
print("The issue is that both XS and S get 'Perfect fit' (100) for all measurements")
print("because they are within the tolerance range (±3cm).")
print("When sorting, Python's sort is STABLE, meaning items with equal scores")
print("maintain their original order from the dictionary.")
print("\nThe size chart dictionary order determines the final ranking!")
