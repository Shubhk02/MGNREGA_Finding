import requests
import sys
import json
from datetime import datetime

class MGNREGAAPITester:
    def __init__(self, base_url="https://mgnrega-dash.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and 'success' in response_data:
                        print(f"   Success: {response_data.get('success')}")
                        if 'data' in response_data and response_data['data']:
                            if isinstance(response_data['data'], list):
                                print(f"   Data count: {len(response_data['data'])}")
                            else:
                                print(f"   Data keys: {list(response_data['data'].keys()) if isinstance(response_data['data'], dict) else 'Non-dict data'}")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                self.failed_tests.append({
                    'name': name,
                    'expected': expected_status,
                    'actual': response.status_code,
                    'response': response.text[:200]
                })

            return success, response.json() if success and response.text else {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout")
            self.failed_tests.append({'name': name, 'error': 'Timeout'})
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({'name': name, 'error': str(e)})
            return False, {}

    def test_root_endpoint(self):
        """Test API root endpoint"""
        return self.run_test("API Root", "GET", "", 200)

    def test_get_districts(self):
        """Test getting all UP districts"""
        success, response = self.run_test(
            "Get UP Districts",
            "GET",
            "districts",
            200,
            params={"state_code": "UP"}
        )
        
        if success and response.get('success') and response.get('data'):
            districts = response['data']
            print(f"   Found {len(districts)} districts")
            if len(districts) > 0:
                sample_district = districts[0]
                required_fields = ['district_code', 'district_name', 'district_name_hi', 'state_code']
                missing_fields = [field for field in required_fields if field not in sample_district]
                if missing_fields:
                    print(f"   ⚠️  Missing fields in district data: {missing_fields}")
                else:
                    print(f"   ✅ District data structure is valid")
                    print(f"   Sample: {sample_district['district_name']} ({sample_district['district_code']})")
        
        return success, response

    def test_current_performance(self, district_code="UP01"):
        """Test getting current performance for a district"""
        success, response = self.run_test(
            f"Current Performance - {district_code}",
            "GET",
            f"district/{district_code}/current",
            200
        )
        
        if success and response.get('success') and response.get('data'):
            data = response['data']
            required_fields = ['district_code', 'total_workers', 'work_completed', 'average_wage', 
                             'budget_allocated', 'budget_spent', 'person_days_generated']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                print(f"   ⚠️  Missing fields in performance data: {missing_fields}")
            else:
                print(f"   ✅ Performance data structure is valid")
                print(f"   Workers: {data.get('total_workers')}, Budget: ₹{data.get('budget_allocated')}")
        
        return success, response

    def test_historical_performance(self, district_code="UP01"):
        """Test getting historical performance for a district"""
        success, response = self.run_test(
            f"Historical Performance - {district_code}",
            "GET",
            f"district/{district_code}/history",
            200,
            params={"months": 6}
        )
        
        if success and response.get('success') and response.get('data'):
            data = response['data']
            print(f"   Historical data points: {len(data)}")
            if len(data) > 0:
                sample_data = data[0]
                required_fields = ['month', 'year', 'total_workers', 'work_completed']
                missing_fields = [field for field in required_fields if field not in sample_data]
                if missing_fields:
                    print(f"   ⚠️  Missing fields in historical data: {missing_fields}")
                else:
                    print(f"   ✅ Historical data structure is valid")
        
        return success, response

    def test_comparison_performance(self, district_code="UP01"):
        """Test getting comparison performance for a district"""
        success, response = self.run_test(
            f"Comparison Performance - {district_code}",
            "GET",
            f"district/{district_code}/compare",
            200
        )
        
        if success and response.get('success') and response.get('data'):
            data = response['data']
            required_sections = ['current', 'previous', 'changes']
            missing_sections = [section for section in required_sections if section not in data]
            if missing_sections:
                print(f"   ⚠️  Missing sections in comparison data: {missing_sections}")
            else:
                print(f"   ✅ Comparison data structure is valid")
                if 'changes' in data:
                    changes = data['changes']
                    print(f"   Sample changes: Workers: {changes.get('total_workers', 0):.1f}%, Budget: {changes.get('budget_spent', 0):.1f}%")
        
        return success, response

    def test_multiple_districts(self):
        """Test multiple districts to ensure consistency"""
        districts_to_test = ["UP01", "UP02", "UP03", "UP49", "UP50"]  # Mix of districts including Lucknow
        successful_districts = 0
        
        for district_code in districts_to_test:
            success, _ = self.test_current_performance(district_code)
            if success:
                successful_districts += 1
        
        print(f"\n📊 Multiple Districts Test: {successful_districts}/{len(districts_to_test)} districts working")
        return successful_districts == len(districts_to_test)

def main():
    print("🚀 Starting MGNREGA Dashboard API Tests")
    print("=" * 50)
    
    tester = MGNREGAAPITester()
    
    # Test sequence
    print("\n1️⃣ Testing API Root...")
    tester.test_root_endpoint()
    
    print("\n2️⃣ Testing Districts Endpoint...")
    districts_success, districts_response = tester.test_get_districts()
    
    print("\n3️⃣ Testing Current Performance...")
    tester.test_current_performance()
    
    print("\n4️⃣ Testing Historical Performance...")
    tester.test_historical_performance()
    
    print("\n5️⃣ Testing Comparison Performance...")
    tester.test_comparison_performance()
    
    print("\n6️⃣ Testing Multiple Districts...")
    tester.test_multiple_districts()
    
    # Print final results
    print("\n" + "=" * 50)
    print("📊 FINAL TEST RESULTS")
    print("=" * 50)
    print(f"✅ Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"❌ Tests failed: {len(tester.failed_tests)}")
    
    if tester.failed_tests:
        print("\n🔍 Failed Tests Details:")
        for i, test in enumerate(tester.failed_tests, 1):
            print(f"{i}. {test['name']}")
            if 'error' in test:
                print(f"   Error: {test['error']}")
            else:
                print(f"   Expected: {test['expected']}, Got: {test['actual']}")
                print(f"   Response: {test['response']}")
    
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Backend API tests mostly successful!")
        return 0
    else:
        print("⚠️  Backend API has significant issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())