# Stock Comparison MCP Server

A Model Context Protocol (MCP) server implementation that demonstrates how to build an MCP for financial data. This server provides stock comparison analytics using TwelveData as the data provider.

## Features

### MCP Tools

The server exposes three main tools via the MCP protocol:

1. `compare_stocks`
   - Fetches and compares multiple stock symbols
   - Returns price metrics, volatility, Sharpe ratios, VAR 95 and correlation matrices
   - Supports customizable intervals and lookback periods

2. `hierarchical_risk_parity_portfolio`
   - Constructs optimal portfolio weights using the HRP algorithm
   - Clusters assets based on correlation distance
   - Allocates risk equally across hierarchical branches

3. `health_check`
   - Simple health endpoint for monitoring

### Implementation Features

- **Caching**: Local filesystem cache for API responses
- **Rate Limiting**: Built-in request delays to respect API limits
- **Error Handling**: Comprehensive error reporting via MCP protocol
- **Type Safety**: Full typing support with runtime validation
- **Metrics**: Returns key financial metrics including:
  - Cumulative returns
  - Annualized volatility
  - Sharpe ratio
  - 95% VaR (Value at Risk)
  - Correlation matrices

## Setup

1. Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create a `.env` file with your TwelveData API key:
```
TWELVE_DATA_API_KEY=your_api_key_here
```


## Usage with VS Code

This MCP server is designed to work seamlessly with VS Code (via GitHub Copilot). Here's how to set it up:

### VS Code Setup

1. Install GitHub Copilot and Copilot Chat extensions
2. Enable MCP server support in settings.json:
```json
{
    "github.copilot.advanced": {
        "mcp.enableStockComparison": true
    }
}
```

3. Create a .vscode folder and add a mcp.json file:
```json
{
  "servers": {
    "stock-comparison": {
      "command": "uv",
      "args": ["run","python", "server/server.py"],
      "cwd": "."
    }
  }
}
```

4. Press Ctrl+Shift+P and select MCP List servers\stock-comparison



Now you can use natural language in Copilot Chat to analyze stocks:
```
Compare a list of 20 stocks for the past 252 trading days.
Then, based on the comparison and analysis, select 10 of those stocks and perform a portfolio optimization using the hierarchical risk parity method.
```

## Cache Configuration

- Cache location: `~/.stock_mcp_cache`
- Quote cache TTL: 15 minutes
- Historical data cache TTL: 1 hour
- Fundamentals cache TTL: 24 hours

## Error Handling

The server provides detailed error messages for common scenarios:
- Missing/invalid API keys
- Rate limiting issues
- Invalid symbols
- Insufficient data for analysis


## License

MIT License
