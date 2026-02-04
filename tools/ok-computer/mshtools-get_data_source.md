# Tool Specification: mshtools-get_data_source

## Overview
Data retrieval from structured sources (finance, economics, academia). Returns data preview and downloadable file.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "data_source_name": {
      "type": "string",
      "enum": ["yahoo_finance", "world_bank_open_data", "arxiv", "google_scholar"]
    },
    "api_name": {
      "type": "string",
      "description": "Specific API endpoint to call"
    },
    "params": {
      "type": "object",
      "description": "API-specific parameters"
    }
  },
  "required": ["data_source_name", "api_name", "params"]
}
```

## Streaming Mechanism
- **Query Execution**: Direct API call to data provider
- **Response**:
  - Data preview (truncated if large)
  - File download path
  - Metadata (record count, time range, etc.)

## Integration Architecture

### Data Providers
- **Yahoo Finance**: Real-time and historical market data
- **World Bank**: 29,000+ global indicators (1960-present)
- **arXiv**: Physics, CS, math preprints
- **Google Scholar**: Citation graphs, author metrics

## Usage Constraints
- **Time Ranges**: Don't fetch entire series for sparse data points
- **Required Params**: Must provide all required API parameters
- **File Path**: Some APIs require file_path in params

## Usage Patterns

### Stock Data
```
get_data_source(
  data_source_name="yahoo_finance",
  api_name="get_historical_stock_prices",
  params={"ticker": "AAPL", "period": "1y", "interval": "1d"}
)
```

### Economic Indicators
```
get_data_source(
  data_source_name="world_bank_open_data",
  api_name="get_indicator",
  params={"indicator": "GDP", "country": "USA", "date": "2010:2020"}
)
```

### Academic Search
```
get_data_source(
  data_source_name="arxiv",
  api_name="search",
  params={"query": "transformer architecture", "max_results": 10}
)
```

## Related Tools
- `get_data_source_desc`: Must call first to understand API parameters
- `ipython`: Use for data analysis after retrieval
