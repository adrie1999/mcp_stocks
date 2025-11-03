#!/usr/bin/env python3
"""
Stock Comparison MCP Server
Transformed from Flask REST API to Model Context Protocol
"""

import asyncio
import json
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp import types

import analyzers

server = Server("stock-comparison")


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available stock data resources"""
    return [
        types.Resource(
            uri="stock://health",
            name="Server Health",
            description="Check server health status",
            mimeType="application/json",
        )
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read stock data resources"""
    if uri == "stock://health":
        health_status = {"status": "ok"}
        return json.dumps(health_status, indent=2)
    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available stock analysis tools"""
    return [
        types.Tool(
            name="compare_stocks",
            description="Compare multiple stock symbols with analysis. Fetches data and compares performance, metrics, and trends.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of stock ticker symbols to compare (e.g., ['AAPL', 'MSFT', 'GOOGL'])",
                        "minItems": 1
                    },
                    "interval": {
                        "type": "string",
                        "description": "Time interval for historical data (e.g., '1day', '1week', '1month'). Optional.",
                        "default": None
                    },
                    "outputsize": {
                        "type": "integer",
                        "description": "Number of data points to retrieve. Optional.",
                        "default": None
                    }
                },
                "required": ["symbols"]
            }
        ),
         types.Tool(
            name="hierarchical_risk_parity_portfolio",
            description="Construct a hierarchical risk parity portfolio, using Scipy hierarchical clustering.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of stock ticker symbols to compare (e.g., ['AAPL', 'MSFT', 'GOOGL'])",
                        "minItems": 1
                    },
                    "interval": {
                        "type": "string",
                        "description": "Time interval for historical data (e.g., '1day', '1week', '1month'). Optional.",
                        "default": None
                    },
                    "outputsize": {
                        "type": "integer",
                        "description": "Number of data points to retrieve. Optional.",
                        "default": None
                    }
                },
                "required": ["symbols"]
            }
        ),
        types.Tool(
            name="health_check",
            description="Check if the stock comparison server is running properly",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, 
    arguments: dict
) -> list[types.TextContent]:
    """Handle tool execution requests"""
    
    try:
        if name == "compare_stocks":
            symbols = arguments.get("symbols", [])
            if not symbols:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "missing symbols parameter, provide list like ['AAPL', 'MSFT']"
                    }, indent=2)
                )]
            
            syms = [s.strip().upper() for s in symbols if s.strip()]
            
            if not syms:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "no valid symbols provided"
                    }, indent=2)
                )]
            
            interval = arguments.get("interval")
            outputsize = arguments.get("outputsize")
            
            if outputsize is not None:
                try:
                    outputsize = int(outputsize)
                except (ValueError, TypeError):
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "error": "outputsize must be an integer"
                        }, indent=2)
                    )]
            
            try:
                result = analyzers.compare_symbols(
                    syms, 
                    interval=interval, 
                    outputsize=outputsize
                )
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            
            except Exception as exc:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Analysis failed: {str(exc)}"
                    }, indent=2)
                )]
        elif name == "hierarchical_risk_parity_portfolio":
            symbols = arguments.get("symbols", [])
            if not symbols:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "missing symbols parameter, provide list like ['AAPL', 'MSFT']"
                    }, indent=2)
                )]
            
            syms = [s.strip().upper() for s in symbols if s.strip()]
            
            if not syms:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "no valid symbols provided"
                    }, indent=2)
                )]
            
            interval = arguments.get("interval")
            outputsize = arguments.get("outputsize")
            
            if outputsize is not None:
                try:
                    outputsize = int(outputsize)
                except (ValueError, TypeError):
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "error": "outputsize must be an integer"
                        }, indent=2)
                    )]
            
            try:
                result = analyzers.hierarchical_risk_parity_portfolio(
                    syms, 
                    interval=interval, 
                    outputsize=outputsize
                )
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            
            except Exception as exc:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Analysis failed: {str(exc)}"
                    }, indent=2)
                )]
        
        
        elif name == "health_check":
            return [types.TextContent(
                type="text",
                text=json.dumps({"status": "ok"}, indent=2)
            )]
        
        else:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Unknown tool: {name}"
                }, indent=2)
            )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": f"Error executing {name}: {str(e)}"
            }, indent=2)
        )]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="stock-comparison",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())