"""Comprehensive test script for all EIA API tools."""
import asyncio
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Set the API key
os.environ["EIA_API_KEY"] = os.getenv("EIA_API_KEY", "")

from eia_mcp.server import handle_tool_call


def print_result(name: str, result: dict, show_sample: bool = True):
    """Helper function to print test results."""
    if "error" in result:
        print(f"   ✗ Error: {result['error']}")
        if "details" in result:
            print(f"     Details: {result['details'][:200]}...")
        return False

    data = result.get("response", {}).get("data", [])
    total = result.get("response", {}).get("total", len(data))
    print(f"   ✓ Success - Retrieved {len(data)} records (total available: {total})")

    if show_sample and data and isinstance(data, list) and len(data) > 0:
        print(f"   Sample: {data[0]}")
    return True


async def test_all_tools():
    """Test all EIA API tools."""
    print("=" * 60)
    print("EIA MCP Server - Comprehensive API Test")
    print("=" * 60)

    passed = 0
    failed = 0

    # ==================== ELECTRICITY TOOLS ====================
    print("\n" + "=" * 60)
    print("ELECTRICITY TOOLS")
    print("=" * 60)

    # Test 1: eia_electricity_retail_sales
    print("\n1. Testing eia_electricity_retail_sales...")
    result = await handle_tool_call("eia_electricity_retail_sales", {
        "state": "CA",
        "sector": "RES",
        "frequency": "annual",
        "start": "2022",
        "end": "2023",
        "limit": 5
    })
    if print_result("eia_electricity_retail_sales", result):
        passed += 1
    else:
        failed += 1

    # Test 2: eia_electricity_operational_data
    print("\n2. Testing eia_electricity_operational_data...")
    result = await handle_tool_call("eia_electricity_operational_data", {
        "state": "TX",
        "fuel_type": "NG",
        "frequency": "annual",
        "start": "2022",
        "end": "2023",
        "limit": 5
    })
    if print_result("eia_electricity_operational_data", result):
        passed += 1
    else:
        failed += 1

    # Test 3: eia_electricity_rto (hourly region data)
    print("\n3. Testing eia_electricity_rto (region-data)...")
    result = await handle_tool_call("eia_electricity_rto", {
        "route": "region-data",
        "respondent": "CISO",
        "limit": 5
    })
    if print_result("eia_electricity_rto", result):
        passed += 1
    else:
        failed += 1

    # Test 3b: eia_electricity_rto (daily fuel type data)
    print("\n3b. Testing eia_electricity_rto (daily-fuel-type-data)...")
    result = await handle_tool_call("eia_electricity_rto", {
        "route": "daily-fuel-type-data",
        "respondent": "CISO",
        "limit": 5
    })
    if print_result("eia_electricity_rto (daily)", result):
        passed += 1
    else:
        failed += 1

    # Test 4: eia_electricity_state_profiles
    print("\n4. Testing eia_electricity_state_profiles...")
    result = await handle_tool_call("eia_electricity_state_profiles", {
        "route": "source-disposition",
        "state": "NY",
        "start": "2022",
        "end": "2023",
        "limit": 5
    })
    if print_result("eia_electricity_state_profiles", result):
        passed += 1
    else:
        failed += 1

    # Test 4b: eia_electricity_state_profiles (emissions)
    print("\n4b. Testing eia_electricity_state_profiles (emissions)...")
    result = await handle_tool_call("eia_electricity_state_profiles", {
        "route": "emissions-by-state-by-fuel",
        "state": "CA",
        "limit": 5
    })
    if print_result("eia_electricity_state_profiles (emissions)", result):
        passed += 1
    else:
        failed += 1

    # Test 5: eia_electricity_generator_capacity
    print("\n5. Testing eia_electricity_generator_capacity...")
    result = await handle_tool_call("eia_electricity_generator_capacity", {
        "state": "CA",
        "energy_source": "SUN",
        "limit": 5
    })
    if print_result("eia_electricity_generator_capacity", result):
        passed += 1
    else:
        failed += 1

    # Test 6: eia_electricity_facility_fuel
    print("\n6. Testing eia_electricity_facility_fuel...")
    result = await handle_tool_call("eia_electricity_facility_fuel", {
        "state": "TX",
        "frequency": "annual",
        "start": "2022",
        "end": "2023",
        "limit": 5
    })
    if print_result("eia_electricity_facility_fuel", result):
        passed += 1
    else:
        failed += 1

    # ==================== NATURAL GAS TOOLS ====================
    print("\n" + "=" * 60)
    print("NATURAL GAS TOOLS")
    print("=" * 60)

    # Test 7: eia_natural_gas_summary
    print("\n7. Testing eia_natural_gas_summary...")
    result = await handle_tool_call("eia_natural_gas_summary", {
        "frequency": "monthly",
        "limit": 5
    })
    if print_result("eia_natural_gas_summary", result):
        passed += 1
    else:
        failed += 1

    # Test 8: eia_natural_gas_prices
    print("\n8. Testing eia_natural_gas_prices...")
    result = await handle_tool_call("eia_natural_gas_prices", {
        "route": "sum",
        "frequency": "monthly",
        "limit": 5
    })
    if print_result("eia_natural_gas_prices", result):
        passed += 1
    else:
        failed += 1

    # Test 9: eia_natural_gas_exploration_reserves
    print("\n9. Testing eia_natural_gas_exploration_reserves...")
    result = await handle_tool_call("eia_natural_gas_exploration_reserves", {
        "route": "wellend",
        "frequency": "annual",
        "limit": 5
    })
    if print_result("eia_natural_gas_exploration_reserves", result):
        passed += 1
    else:
        failed += 1

    # Test 10: eia_natural_gas_production
    print("\n10. Testing eia_natural_gas_production...")
    result = await handle_tool_call("eia_natural_gas_production", {
        "route": "sum",
        "frequency": "monthly",
        "limit": 5
    })
    if print_result("eia_natural_gas_production", result):
        passed += 1
    else:
        failed += 1

    # Test 11: eia_natural_gas_imports_exports
    print("\n11. Testing eia_natural_gas_imports_exports...")
    result = await handle_tool_call("eia_natural_gas_imports_exports", {
        "route": "state",
        "frequency": "monthly",
        "limit": 5
    })
    if print_result("eia_natural_gas_imports_exports", result):
        passed += 1
    else:
        failed += 1

    # Test 12: eia_natural_gas_storage
    print("\n12. Testing eia_natural_gas_storage (weekly)...")
    result = await handle_tool_call("eia_natural_gas_storage", {
        "route": "wkly",
        "frequency": "weekly",
        "limit": 5
    })
    if print_result("eia_natural_gas_storage (weekly)", result):
        passed += 1
    else:
        failed += 1

    # Test 12b: eia_natural_gas_storage (summary)
    print("\n12b. Testing eia_natural_gas_storage (summary)...")
    result = await handle_tool_call("eia_natural_gas_storage", {
        "route": "sum",
        "frequency": "monthly",
        "limit": 5
    })
    if print_result("eia_natural_gas_storage (summary)", result):
        passed += 1
    else:
        failed += 1

    # Test 13: eia_natural_gas_consumption
    print("\n13. Testing eia_natural_gas_consumption...")
    result = await handle_tool_call("eia_natural_gas_consumption", {
        "route": "sum",
        "frequency": "monthly",
        "limit": 5
    })
    if print_result("eia_natural_gas_consumption", result):
        passed += 1
    else:
        failed += 1

    # ==================== EXPLORATION TOOL ====================
    print("\n" + "=" * 60)
    print("EXPLORATION TOOL")
    print("=" * 60)

    # Test 14: eia_explore_routes (root)
    print("\n14. Testing eia_explore_routes (root)...")
    result = await handle_tool_call("eia_explore_routes", {
        "path": ""
    })
    if "error" not in result:
        routes = result.get("response", {}).get("routes", [])
        print(f"   ✓ Success - Found {len(routes)} top-level routes")
        print(f"   Routes: {[r.get('id') for r in routes]}")
        passed += 1
    else:
        print(f"   ✗ Error: {result['error']}")
        failed += 1

    # Test 14b: eia_explore_routes (electricity)
    print("\n14b. Testing eia_explore_routes (electricity)...")
    result = await handle_tool_call("eia_explore_routes", {
        "path": "electricity"
    })
    if "error" not in result:
        routes = result.get("response", {}).get("routes", [])
        print(f"   ✓ Success - Found {len(routes)} electricity routes")
        route_ids = [r.get('id') for r in routes[:10]]
        print(f"   Sample routes: {route_ids}")
        passed += 1
    else:
        print(f"   ✗ Error: {result['error']}")
        failed += 1

    # Test 14c: eia_explore_routes (natural-gas)
    print("\n14c. Testing eia_explore_routes (natural-gas)...")
    result = await handle_tool_call("eia_explore_routes", {
        "path": "natural-gas"
    })
    if "error" not in result:
        routes = result.get("response", {}).get("routes", [])
        print(f"   ✓ Success - Found {len(routes)} natural-gas routes")
        route_ids = [r.get('id') for r in routes[:10]]
        print(f"   Sample routes: {route_ids}")
        passed += 1
    else:
        print(f"   ✗ Error: {result['error']}")
        failed += 1

    # ==================== EDGE CASES ====================
    print("\n" + "=" * 60)
    print("EDGE CASES")
    print("=" * 60)

    # Test 15: Unknown tool
    print("\n15. Testing unknown tool handling...")
    result = await handle_tool_call("eia_unknown_tool", {})
    if "error" in result and "Unknown tool" in result["error"]:
        print(f"   ✓ Correctly handled unknown tool: {result['error']}")
        passed += 1
    else:
        print(f"   ✗ Did not handle unknown tool correctly")
        failed += 1

    # Test 16: Empty parameters
    print("\n16. Testing with minimal parameters...")
    result = await handle_tool_call("eia_electricity_retail_sales", {
        "limit": 3
    })
    if print_result("eia_electricity_retail_sales (minimal params)", result):
        passed += 1
    else:
        failed += 1

    # ==================== SUMMARY ====================
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    total = passed + failed
    print(f"\nTotal tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {passed/total*100:.1f}%")

    if failed == 0:
        print("\n✓ All tests passed!")
    else:
        print(f"\n✗ {failed} test(s) failed")

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(test_all_tools())
    exit(0 if success else 1)
