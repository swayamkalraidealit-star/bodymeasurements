"""Quick test script for avatar and fit analysis endpoints."""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_avatar_generation():
    """Test avatar generation endpoint."""
    print("\n🧪 Testing Avatar Generation...")
    
    payload = {
        "measurements": {
            "height": 175,
            "shoulder_width": 45,
            "chest": 95,
            "waist": 80,
            "hip": 95,
            "inseam": 80,
            "units": "cm"
        },
        "skin_tone": "medium",
        "gender": "neutral"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/avatar/generate", json=payload)
        response.raise_for_status()
        result = response.json()
        
        print("✅ Avatar generated successfully!")
        print(f"   Avatar ID: {result['avatar_id']}")
        print(f"   Timestamp: {result['timestamp']}")
        
        return result['avatar_id']
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_fit_analysis(avatar_id=None):
    """Test fit analysis endpoint."""
    print("\n🧪 Testing Fit Analysis...")
    
    payload = {
        "measurements": {
            "height": 175,
            "shoulder_width": 45,
            "chest": 95,
            "waist": 80,
            "hip": 95,
            "inseam": 80,
            "units": "cm"
        },
        "garment_id": "tshirt_basic_001",
        "garment_size": "M"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/fit/analyze", json=payload)
        response.raise_for_status()
        result = response.json()
        
        print("✅ Fit analysis completed!")
        print(f"   Overall fit score: {result['overall_fit_score']}/100")
        print(f"   Overall category: {result['overall_fit_category']}")
        print(f"   Zones analyzed: {len(result['zones'])}")
        
        for zone in result['zones']:
            print(f"   - {zone['zone']}: {zone['fit_category']} (score: {zone['fit_score']})")
        
        print("\n   Recommendations:")
        for rec in result['recommendations']:
            print(f"   {rec}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_try_on(avatar_id):
    """Test virtual try-on endpoint."""
    if not avatar_id:
        print("\n⚠️  Skipping try-on test (no avatar ID)")
        return
    
    print("\n🧪 Testing Virtual Try-On...")
    
    payload = {
        "avatar_id": avatar_id,
        "garment_id": "tshirt_basic_001",
        "garment_size": "M"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/tryon/simulate", json=payload)
        response.raise_for_status()
        result = response.json()
        
        print("✅ Try-on simulation completed!")
        print(f"   Garment applied: {result['garment_info']['garment_id']}")
        print(f"   Size: {result['garment_info']['size']}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_list_garments():
    """Test garment listing endpoint."""
    print("\n🧪 Testing Garment Listing...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/fit/garments")
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Found {result['total_count']} garments:")
        for garment in result['garments']:
            print(f"   - {garment['name']} ({garment['id']})")
            print(f"     Sizes: {', '.join(garment['available_sizes'])}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Avatar & Try-On System Test Suite")
    print("=" * 60)
    
    # Test avatar generation
    avatar_id = test_avatar_generation()
    
    # Test fit analysis
    test_fit_analysis(avatar_id)
    
    # Test virtual try-on
    test_try_on(avatar_id)
    
    # Test garment listing
    test_list_garments()
    
    print("\n" + "=" * 60)
    print("Test Suite Complete!")
    print("=" * 60)
