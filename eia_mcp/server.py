"""EIA MCP Server - Energy Information Administration API integration."""

import os
import json
from typing import Any
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# EIA API Configuration
EIA_API_BASE = "https://api.eia.gov/v2"
EIA_API_KEY = os.environ.get("EIA_API_KEY", "")

server = Server("eia-mcp")


async def make_eia_request(
    endpoint: str,
    params: dict[str, Any] | None = None,
    data_columns: list[str] | None = None,
    facets: dict[str, list[str]] | None = None,
    frequency: str | None = None,
    start: str | None = None,
    end: str | None = None,
    sort: list[dict[str, str]] | None = None,
    offset: int = 0,
    length: int = 100,
    get_data: bool = True,
) -> dict[str, Any]:
    """Make a request to the EIA API."""
    if not EIA_API_KEY:
        return {"error": "EIA_API_KEY environment variable not set"}

    # Append /data to get actual data records (not just metadata)
    if get_data and endpoint and not endpoint.endswith("/data"):
        url = f"{EIA_API_BASE}/{endpoint}/data"
    else:
        url = f"{EIA_API_BASE}/{endpoint}"

    query_params: dict[str, Any] = {
        "api_key": EIA_API_KEY,
        "offset": offset,
        "length": length,
    }

    if params:
        query_params.update(params)

    if data_columns:
        for col in data_columns:
            query_params.setdefault("data[]", []).append(col) if isinstance(query_params.get("data[]"), list) else None
            if "data[]" not in query_params:
                query_params["data[]"] = data_columns
                break

    if facets:
        for facet_name, facet_values in facets.items():
            query_params[f"facets[{facet_name}][]"] = facet_values

    if frequency:
        query_params["frequency"] = frequency

    if start:
        query_params["start"] = start

    if end:
        query_params["end"] = end

    if sort:
        for i, sort_item in enumerate(sort):
            for key, value in sort_item.items():
                query_params[f"sort[{i}][{key}]"] = value

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, params=query_params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
        except httpx.RequestError as e:
            return {"error": f"Request error: {str(e)}"}
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response"}


# ============== ELECTRICITY TOOLS ==============

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available EIA tools."""
    return [
        # Electricity Tools
        Tool(
            name="eia_electricity_retail_sales",
            description="Get electricity retail sales data including sales to customers by state and sector, customer counts, and pricing. Sources: Forms EIA-826, EIA-861, EIA-861M",
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "description": "State code (e.g., 'CA', 'TX', 'NY'). Leave empty for all states."
                    },
                    "sector": {
                        "type": "string",
                        "description": "Sector ID: RES (residential), COM (commercial), IND (industrial), TRA (transportation), OTH (other), ALL (all sectors)",
                        "enum": ["RES", "COM", "IND", "TRA", "OTH", "ALL"]
                    },
                    "frequency": {
                        "type": "string",
                        "description": "Data frequency",
                        "enum": ["monthly", "quarterly", "annual"]
                    },
                    "start": {
                        "type": "string",
                        "description": "Start date (YYYY-MM for monthly, YYYY for annual)"
                    },
                    "end": {
                        "type": "string",
                        "description": "End date (YYYY-MM for monthly, YYYY for annual)"
                    },
                    "data_columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Data columns to retrieve (e.g., 'revenue', 'sales', 'price', 'customers')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of records to return (default: 100, max: 5000)"
                    }
                }
            }
        ),
        Tool(
            name="eia_electricity_operational_data",
            description="Get monthly and annual electric power operational data including generation, fuel consumption, and emissions by state, sector, and energy source. Source: Form EIA-923",
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "description": "State code (e.g., 'CA', 'TX')"
                    },
                    "fuel_type": {
                        "type": "string",
                        "description": "Fuel type code (e.g., 'NG' for natural gas, 'COL' for coal, 'NUC' for nuclear, 'SUN' for solar, 'WND' for wind)"
                    },
                    "frequency": {
                        "type": "string",
                        "description": "Data frequency",
                        "enum": ["monthly", "annual"]
                    },
                    "start": {
                        "type": "string",
                        "description": "Start date"
                    },
                    "end": {
                        "type": "string",
                        "description": "End date"
                    },
                    "data_columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Data columns to retrieve (e.g., 'generation', 'total-consumption')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of records (default: 100)"
                    }
                }
            }
        ),
        Tool(
            name="eia_electricity_rto",
            description="Get hourly and daily electric power operations by balancing authority (Regional Transmission Operator). Includes demand, generation, and interchange data. Source: Form EIA-930",
            inputSchema={
                "type": "object",
                "properties": {
                    "route": {
                        "type": "string",
                        "description": "RTO data route",
                        "enum": ["region-data", "region-sub-ba-data", "fuel-type-data", "interchange-data", "daily-region-data", "daily-region-sub-ba-data", "daily-fuel-type-data", "daily-interchange-data"]
                    },
                    "respondent": {
                        "type": "string",
                        "description": "Balancing authority code (e.g., 'CISO' for California ISO, 'PJM', 'MISO', 'ERCOT')"
                    },
                    "fuel_type": {
                        "type": "string",
                        "description": "Fuel type for generation data"
                    },
                    "start": {
                        "type": "string",
                        "description": "Start datetime (YYYY-MM-DDTHH)"
                    },
                    "end": {
                        "type": "string",
                        "description": "End datetime (YYYY-MM-DDTHH)"
                    },
                    "data_columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Data columns (e.g., 'value' for demand/generation values)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of records (default: 100)"
                    }
                }
            }
        ),
        Tool(
            name="eia_electricity_state_profiles",
            description="Get state-level electricity profiles including generation mix, consumption patterns, and infrastructure data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "route": {
                        "type": "string",
                        "description": "Profile data route",
                        "enum": ["emissions-by-state-by-fuel", "source-disposition", "capability", "net-metering", "meters"]
                    },
                    "state": {
                        "type": "string",
                        "description": "State code (e.g., 'CA', 'TX')"
                    },
                    "start": {
                        "type": "string",
                        "description": "Start year"
                    },
                    "end": {
                        "type": "string",
                        "description": "End year"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of records (default: 100)"
                    }
                }
            }
        ),
        Tool(
            name="eia_electricity_generator_capacity",
            description="Get inventory of operable generators in the U.S. including capacity, technology type, and status. Sources: Forms EIA-860, EIA-860M",
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "description": "State code"
                    },
                    "status": {
                        "type": "string",
                        "description": "Generator status code"
                    },
                    "technology": {
                        "type": "string",
                        "description": "Technology type"
                    },
                    "energy_source": {
                        "type": "string",
                        "description": "Primary energy source code"
                    },
                    "start": {
                        "type": "string",
                        "description": "Start period"
                    },
                    "end": {
                        "type": "string",
                        "description": "End period"
                    },
                    "data_columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Data columns (e.g., 'nameplate-capacity-mw', 'net-summer-capacity-mw')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of records (default: 100)"
                    }
                }
            }
        ),
        Tool(
            name="eia_electricity_facility_fuel",
            description="Get annual and monthly operational data for individual power plants by energy source and equipment type. Source: Form EIA-923",
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "description": "State code"
                    },
                    "plant_id": {
                        "type": "string",
                        "description": "Specific plant ID"
                    },
                    "fuel_type": {
                        "type": "string",
                        "description": "Fuel type code"
                    },
                    "frequency": {
                        "type": "string",
                        "description": "Data frequency",
                        "enum": ["monthly", "quarterly", "annual"]
                    },
                    "start": {
                        "type": "string",
                        "description": "Start period"
                    },
                    "end": {
                        "type": "string",
                        "description": "End period"
                    },
                    "data_columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Data columns (e.g., 'generation', 'gross-generation', 'consumption-for-eg', 'total-consumption')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of records (default: 100)"
                    }
                }
            }
        ),
        # Natural Gas Tools
        Tool(
            name="eia_natural_gas_summary",
            description="Get natural gas summary data providing an overview of the natural gas survey information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "series": {
                        "type": "string",
                        "description": "Data series to retrieve"
                    },
                    "frequency": {
                        "type": "string",
                        "description": "Data frequency",
                        "enum": ["weekly", "monthly", "annual"]
                    },
                    "start": {
                        "type": "string",
                        "description": "Start period"
                    },
                    "end": {
                        "type": "string",
                        "description": "End period"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of records (default: 100)"
                    }
                }
            }
        ),
        Tool(
            name="eia_natural_gas_prices",
            description="Get natural gas price data including spot prices, futures, citygate prices, residential, commercial, and industrial prices.",
            inputSchema={
                "type": "object",
                "properties": {
                    "route": {
                        "type": "string",
                        "description": "Price data route (e.g., 'sum' for summary prices)"
                    },
                    "area": {
                        "type": "string",
                        "description": "Geographic area or state code"
                    },
                    "product": {
                        "type": "string",
                        "description": "Product type"
                    },
                    "frequency": {
                        "type": "string",
                        "description": "Data frequency",
                        "enum": ["daily", "weekly", "monthly", "annual"]
                    },
                    "start": {
                        "type": "string",
                        "description": "Start period"
                    },
                    "end": {
                        "type": "string",
                        "description": "End period"
                    },
                    "data_columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Data columns to retrieve (e.g., 'value')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of records (default: 100)"
                    }
                }
            }
        ),
        Tool(
            name="eia_natural_gas_exploration_reserves",
            description="Get natural gas exploration and reserves data including resource discovery and stockpile levels.",
            inputSchema={
                "type": "object",
                "properties": {
                    "route": {
                        "type": "string",
                        "description": "Data route (e.g., 'wellend', 'drygase', 'crudeoilprov', 'welldrills')"
                    },
                    "area": {
                        "type": "string",
                        "description": "Geographic area"
                    },
                    "frequency": {
                        "type": "string",
                        "description": "Data frequency",
                        "enum": ["monthly", "annual"]
                    },
                    "start": {
                        "type": "string",
                        "description": "Start period"
                    },
                    "end": {
                        "type": "string",
                        "description": "End period"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of records (default: 100)"
                    }
                }
            }
        ),
        Tool(
            name="eia_natural_gas_production",
            description="Get natural gas production data including output metrics and production volumes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "route": {
                        "type": "string",
                        "description": "Production data route (e.g., 'sum', 'lngwprp', 'oilwprr', 'whv')"
                    },
                    "area": {
                        "type": "string",
                        "description": "Geographic area or state code"
                    },
                    "product": {
                        "type": "string",
                        "description": "Product type"
                    },
                    "frequency": {
                        "type": "string",
                        "description": "Data frequency",
                        "enum": ["monthly", "annual"]
                    },
                    "start": {
                        "type": "string",
                        "description": "Start period"
                    },
                    "end": {
                        "type": "string",
                        "description": "End period"
                    },
                    "data_columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Data columns to retrieve"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of records (default: 100)"
                    }
                }
            }
        ),
        Tool(
            name="eia_natural_gas_imports_exports",
            description="Get natural gas imports, exports, and pipeline movement data including cross-border flows and distribution infrastructure.",
            inputSchema={
                "type": "object",
                "properties": {
                    "route": {
                        "type": "string",
                        "description": "Movement data route (e.g., 'impc', 'expc', 'poe1', 'state', 'ist')"
                    },
                    "area": {
                        "type": "string",
                        "description": "Geographic area"
                    },
                    "country": {
                        "type": "string",
                        "description": "Country for import/export data"
                    },
                    "frequency": {
                        "type": "string",
                        "description": "Data frequency",
                        "enum": ["monthly", "annual"]
                    },
                    "start": {
                        "type": "string",
                        "description": "Start period"
                    },
                    "end": {
                        "type": "string",
                        "description": "End period"
                    },
                    "data_columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Data columns to retrieve"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of records (default: 100)"
                    }
                }
            }
        ),
        Tool(
            name="eia_natural_gas_storage",
            description="Get natural gas storage data including inventory levels, injections, and withdrawals from storage facilities.",
            inputSchema={
                "type": "object",
                "properties": {
                    "route": {
                        "type": "string",
                        "description": "Storage data route (e.g., 'sum', 'base', 'wkly', 'lngwstor', 'stscd')"
                    },
                    "area": {
                        "type": "string",
                        "description": "Geographic area or region"
                    },
                    "frequency": {
                        "type": "string",
                        "description": "Data frequency",
                        "enum": ["weekly", "monthly", "annual"]
                    },
                    "start": {
                        "type": "string",
                        "description": "Start period"
                    },
                    "end": {
                        "type": "string",
                        "description": "End period"
                    },
                    "data_columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Data columns to retrieve"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of records (default: 100)"
                    }
                }
            }
        ),
        Tool(
            name="eia_natural_gas_consumption",
            description="Get natural gas consumption and end use data including demand patterns by sector (residential, commercial, industrial, electric power).",
            inputSchema={
                "type": "object",
                "properties": {
                    "route": {
                        "type": "string",
                        "description": "Consumption data route (e.g., 'sum', 'num', 'pns', 'acct')"
                    },
                    "area": {
                        "type": "string",
                        "description": "Geographic area or state code"
                    },
                    "sector": {
                        "type": "string",
                        "description": "Sector (e.g., 'RES' for residential, 'COM' for commercial)"
                    },
                    "frequency": {
                        "type": "string",
                        "description": "Data frequency",
                        "enum": ["monthly", "annual"]
                    },
                    "start": {
                        "type": "string",
                        "description": "Start period"
                    },
                    "end": {
                        "type": "string",
                        "description": "End period"
                    },
                    "data_columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Data columns to retrieve"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of records (default: 100)"
                    }
                }
            }
        ),
        # Generic exploration tool
        Tool(
            name="eia_explore_routes",
            description="Explore available EIA API routes and their metadata. Use this to discover available data series, facets, and parameters for any endpoint.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "API path to explore (e.g., 'electricity', 'natural-gas', 'electricity/retail-sales', 'natural-gas/pri')"
                    }
                },
                "required": ["path"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        result = await handle_tool_call(name, arguments)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def handle_tool_call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Route tool calls to appropriate handlers."""

    # Electricity tools
    if name == "eia_electricity_retail_sales":
        endpoint = "electricity/retail-sales"
        facets = {}
        if arguments.get("state"):
            facets["stateid"] = [arguments["state"]]
        if arguments.get("sector"):
            facets["sectorid"] = [arguments["sector"]]

        # Default data columns if not specified
        data_columns = arguments.get("data_columns") or ["revenue", "sales", "price", "customers"]

        return await make_eia_request(
            endpoint=endpoint,
            data_columns=data_columns,
            facets=facets if facets else None,
            frequency=arguments.get("frequency"),
            start=arguments.get("start"),
            end=arguments.get("end"),
            length=arguments.get("limit", 100),
        )

    elif name == "eia_electricity_operational_data":
        endpoint = "electricity/electric-power-operational-data"
        facets = {}
        if arguments.get("state"):
            facets["location"] = [arguments["state"]]
        if arguments.get("fuel_type"):
            facets["fueltypeid"] = [arguments["fuel_type"]]

        data_columns = arguments.get("data_columns") or ["generation", "total-consumption"]

        return await make_eia_request(
            endpoint=endpoint,
            data_columns=data_columns,
            facets=facets if facets else None,
            frequency=arguments.get("frequency"),
            start=arguments.get("start"),
            end=arguments.get("end"),
            length=arguments.get("limit", 100),
        )

    elif name == "eia_electricity_rto":
        route = arguments.get("route", "region-data")
        endpoint = f"electricity/rto/{route}"
        facets = {}
        if arguments.get("respondent"):
            facets["respondent"] = [arguments["respondent"]]
        if arguments.get("fuel_type"):
            facets["fueltype"] = [arguments["fuel_type"]]

        data_columns = arguments.get("data_columns") or ["value"]

        return await make_eia_request(
            endpoint=endpoint,
            data_columns=data_columns,
            facets=facets if facets else None,
            start=arguments.get("start"),
            end=arguments.get("end"),
            length=arguments.get("limit", 100),
        )

    elif name == "eia_electricity_state_profiles":
        route = arguments.get("route", "source-disposition")
        endpoint = f"electricity/state-electricity-profiles/{route}"
        facets = {}
        if arguments.get("state"):
            # Different routes use different facet names for state
            if route == "emissions-by-state-by-fuel":
                facets["stateid"] = [arguments["state"]]
            else:
                facets["state"] = [arguments["state"]]

        # Default columns vary by route
        if arguments.get("data_columns"):
            data_columns = arguments["data_columns"]
        elif route == "emissions-by-state-by-fuel":
            data_columns = ["co2-thousand-metric-tons", "so2-short-tons", "nox-short-tons"]
        elif route == "source-disposition":
            data_columns = ["electric-utilities", "independent-power-producers", "combined-heat-and-pwr-elect"]
        elif route == "capability":
            data_columns = ["capability"]
        else:
            data_columns = ["value"]

        return await make_eia_request(
            endpoint=endpoint,
            data_columns=data_columns,
            facets=facets if facets else None,
            start=arguments.get("start"),
            end=arguments.get("end"),
            length=arguments.get("limit", 100),
        )

    elif name == "eia_electricity_generator_capacity":
        endpoint = "electricity/operating-generator-capacity"
        facets = {}
        if arguments.get("state"):
            facets["stateid"] = [arguments["state"]]
        if arguments.get("status"):
            facets["status"] = [arguments["status"]]
        if arguments.get("technology"):
            facets["technology"] = [arguments["technology"]]
        if arguments.get("energy_source"):
            facets["energy_source_code"] = [arguments["energy_source"]]

        data_columns = arguments.get("data_columns") or ["nameplate-capacity-mw", "net-summer-capacity-mw"]

        return await make_eia_request(
            endpoint=endpoint,
            data_columns=data_columns,
            facets=facets if facets else None,
            start=arguments.get("start"),
            end=arguments.get("end"),
            length=arguments.get("limit", 100),
        )

    elif name == "eia_electricity_facility_fuel":
        endpoint = "electricity/facility-fuel"
        facets = {}
        if arguments.get("state"):
            facets["state"] = [arguments["state"]]
        if arguments.get("plant_id"):
            facets["plantCode"] = [arguments["plant_id"]]
        if arguments.get("fuel_type"):
            facets["fuel2002"] = [arguments["fuel_type"]]

        data_columns = arguments.get("data_columns") or ["generation", "gross-generation", "total-consumption"]

        return await make_eia_request(
            endpoint=endpoint,
            data_columns=data_columns,
            facets=facets if facets else None,
            frequency=arguments.get("frequency"),
            start=arguments.get("start"),
            end=arguments.get("end"),
            length=arguments.get("limit", 100),
        )

    # Natural Gas tools
    elif name == "eia_natural_gas_summary":
        endpoint = "natural-gas/sum/snd"  # Use specific sub-route for data
        facets = {}
        if arguments.get("series"):
            facets["series"] = [arguments["series"]]

        data_columns = arguments.get("data_columns") or ["value"]

        return await make_eia_request(
            endpoint=endpoint,
            data_columns=data_columns,
            facets=facets if facets else None,
            frequency=arguments.get("frequency"),
            start=arguments.get("start"),
            end=arguments.get("end"),
            length=arguments.get("limit", 100),
        )

    elif name == "eia_natural_gas_prices":
        route = arguments.get("route", "sum")
        endpoint = f"natural-gas/pri/{route}"
        facets = {}
        if arguments.get("area"):
            facets["duoarea"] = [arguments["area"]]
        if arguments.get("product"):
            facets["product"] = [arguments["product"]]

        data_columns = arguments.get("data_columns") or ["value"]

        return await make_eia_request(
            endpoint=endpoint,
            data_columns=data_columns,
            facets=facets if facets else None,
            frequency=arguments.get("frequency"),
            start=arguments.get("start"),
            end=arguments.get("end"),
            length=arguments.get("limit", 100),
        )

    elif name == "eia_natural_gas_exploration_reserves":
        route = arguments.get("route", "wellend")
        endpoint = f"natural-gas/enr/{route}"
        facets = {}
        if arguments.get("area"):
            facets["duoarea"] = [arguments["area"]]

        data_columns = arguments.get("data_columns") or ["value"]

        return await make_eia_request(
            endpoint=endpoint,
            data_columns=data_columns,
            facets=facets if facets else None,
            frequency=arguments.get("frequency"),
            start=arguments.get("start"),
            end=arguments.get("end"),
            length=arguments.get("limit", 100),
        )

    elif name == "eia_natural_gas_production":
        route = arguments.get("route", "sum")
        endpoint = f"natural-gas/prod/{route}"
        facets = {}
        if arguments.get("area"):
            facets["duoarea"] = [arguments["area"]]
        if arguments.get("product"):
            facets["product"] = [arguments["product"]]

        data_columns = arguments.get("data_columns") or ["value"]

        return await make_eia_request(
            endpoint=endpoint,
            data_columns=data_columns,
            facets=facets if facets else None,
            frequency=arguments.get("frequency"),
            start=arguments.get("start"),
            end=arguments.get("end"),
            length=arguments.get("limit", 100),
        )

    elif name == "eia_natural_gas_imports_exports":
        route = arguments.get("route", "state")
        endpoint = f"natural-gas/move/{route}"
        facets = {}
        if arguments.get("area"):
            facets["duoarea"] = [arguments["area"]]
        if arguments.get("country"):
            facets["countrynd"] = [arguments["country"]]

        data_columns = arguments.get("data_columns") or ["value"]

        return await make_eia_request(
            endpoint=endpoint,
            data_columns=data_columns,
            facets=facets if facets else None,
            frequency=arguments.get("frequency"),
            start=arguments.get("start"),
            end=arguments.get("end"),
            length=arguments.get("limit", 100),
        )

    elif name == "eia_natural_gas_storage":
        route = arguments.get("route", "sum")
        endpoint = f"natural-gas/stor/{route}"
        facets = {}
        if arguments.get("area"):
            facets["duoarea"] = [arguments["area"]]

        data_columns = arguments.get("data_columns") or ["value"]

        return await make_eia_request(
            endpoint=endpoint,
            data_columns=data_columns,
            facets=facets if facets else None,
            frequency=arguments.get("frequency"),
            start=arguments.get("start"),
            end=arguments.get("end"),
            length=arguments.get("limit", 100),
        )

    elif name == "eia_natural_gas_consumption":
        route = arguments.get("route", "sum")
        endpoint = f"natural-gas/cons/{route}"
        facets = {}
        if arguments.get("area"):
            facets["duoarea"] = [arguments["area"]]
        if arguments.get("sector"):
            facets["process"] = [arguments["sector"]]

        data_columns = arguments.get("data_columns") or ["value"]

        return await make_eia_request(
            endpoint=endpoint,
            data_columns=data_columns,
            facets=facets if facets else None,
            frequency=arguments.get("frequency"),
            start=arguments.get("start"),
            end=arguments.get("end"),
            length=arguments.get("limit", 100),
        )

    # Exploration tool - returns metadata, not data
    elif name == "eia_explore_routes":
        path = arguments.get("path", "")
        endpoint = path if path else ""
        return await make_eia_request(endpoint=endpoint, length=1, get_data=False)

    else:
        return {"error": f"Unknown tool: {name}"}


async def run_server():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main():
    """Main entry point."""
    import asyncio
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
