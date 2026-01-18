# EIA MCP Server

An MCP (Model Context Protocol) server for the U.S. Energy Information Administration (EIA) API, providing access to electricity and natural gas data.

## Features

### Electricity Data
- **Retail Sales** - Sales to customers by state and sector, pricing, and customer counts
- **Operational Data** - Monthly/annual generation, fuel consumption, and emissions
- **RTO Data** - Hourly/daily operations by balancing authority (CISO, PJM, MISO, ERCOT, etc.)
- **State Profiles** - State-level electricity profiles and infrastructure data
- **Generator Capacity** - Inventory of operable generators in the U.S.
- **Facility Fuel** - Individual power plant operational data

### Natural Gas Data
- **Summary** - Overview of natural gas survey data
- **Prices** - Spot prices, futures, citygate, residential, commercial, industrial prices
- **Exploration & Reserves** - Resource discovery and stockpile levels
- **Production** - Output metrics and production volumes
- **Imports/Exports** - Cross-border flows and pipeline movement data
- **Storage** - Inventory levels, injections, and withdrawals
- **Consumption** - End use data by sector

## Installation

```bash
cd eia-mcp
pip install -e .
```

## Configuration

1. Get an API key from [EIA Open Data](https://www.eia.gov/opendata/)
2. Set the environment variable:
   ```bash
   export EIA_API_KEY=your_api_key_here
   ```

## Usage with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "eia": {
      "command": "python",
      "args": ["-m", "eia_mcp.server"],
      "cwd": "/Users/yanpan/eia-mcp",
      "env": {
        "EIA_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Or if installed as a package:

```json
{
  "mcpServers": {
    "eia": {
      "command": "eia-mcp",
      "env": {
        "EIA_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `eia_electricity_retail_sales` | Get electricity retail sales data by state and sector |
| `eia_electricity_operational_data` | Get power generation and fuel consumption data |
| `eia_electricity_rto` | Get real-time grid operations by balancing authority |
| `eia_electricity_state_profiles` | Get state-level electricity profiles |
| `eia_electricity_generator_capacity` | Get generator inventory and capacity data |
| `eia_electricity_facility_fuel` | Get individual power plant data |
| `eia_natural_gas_summary` | Get natural gas summary data |
| `eia_natural_gas_prices` | Get natural gas price data |
| `eia_natural_gas_exploration_reserves` | Get exploration and reserves data |
| `eia_natural_gas_production` | Get production data |
| `eia_natural_gas_imports_exports` | Get import/export and pipeline data |
| `eia_natural_gas_storage` | Get storage facility data |
| `eia_natural_gas_consumption` | Get consumption data by sector |
| `eia_explore_routes` | Explore available API routes and metadata |

## Example Queries

### Get California electricity retail sales
```
Use eia_electricity_retail_sales with state="CA", frequency="monthly", start="2024-01"
```

### Get real-time ERCOT grid data
```
Use eia_electricity_rto with respondent="ERCO", route="region-data"
```

### Get natural gas storage levels
```
Use eia_natural_gas_storage with route="wkly", frequency="weekly"
```

### Explore available routes
```
Use eia_explore_routes with path="electricity" to see all electricity sub-routes
```

## API Reference

Base URL: `https://api.eia.gov/v2/`

For full API documentation, visit: https://www.eia.gov/opendata/documentation.php
