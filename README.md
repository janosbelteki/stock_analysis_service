# Stock Analysis Service

This project provides a microservice for collecting, processing, and analyzing stock prices and volume.

## Considerations of choosing this project
1. Personally I am fascinated by stock exchanges, and I have heard there are all sorts of API for accessing stock data.
2. Based on #1, I would like to better understand day trading, this seemed like an opportunity to start delving deeper into stock data analysis.
3. For the technology, I chose Flask and SQLite due to both of them seeming to be lightweight and easy to learn. I haven't used them beforehand, wanted to try.

## Features
1. Collects stock data from the Yahoo Finance API.
2. For 7-day(5 workday) and 30-day periods, calculates and returns:
   - basic features (linear trend, volatility, average daily return) for all price types.
   - total return (not taking potential dividends into account) and risk reward ratio for close prices
   - correlation coefficient between the selected stock and the top performing (by dollar volume) stock - if selected stock is the top, then for the second in rank
3. Provides a REST API for accessing raw data.

## API (matching stated features)
1. Collect stock data
    path: POST http://127.0.0.1:5000/collect
    params: -
    request body: 
        {
            "symbols": [ str ]   // List of stock symbols to download from the Yahoo Finance API
        }
    response body:
        {
            "status": str,                                                           // The status of the operation (e.g., "success" or "error").
            "message": str                                                           // A descriptive message providing details about the result.
        }
2. Analyze stock data
    path: GET http://127.0.0.1:5000/analyze/{symbol}
    params: -
    request body: -
    response body:
        {
            "close":
                {
                    TOP_STOCK_SYMBOL+"_correlation_coeff":  dict{str : float64}      // Current stock's and top performing stock's Pearson correlation coefficients for a period (7 or 30 days) 
                    "avg_daily_return":  dict{str : float64}                         // Average daily return of current stock price for a period (7 or 30 days)
                    "risk_reward_ratio":  dict{str : float64}                        // Risk reward ratio of current stock price for a period (7 or 30 days)
                    "total_return":  dict{str : float64}                             // Total return of current stock price for a period (7 or 30 days)
                    "trend":  dict{str : float64}                                    // Slope of linear fit of current stock price for a period (7 or 30 days)
                    "volatility":  dict{str : float64}                               // Volatility of current stock price for a period (7 or 30 days)
            },
            "high":
                {
                    "avg_daily_return":  dict{str : float64}                         // Average daily return of current stock price for a period (7 or 30 days)
                    "trend":  dict{str : float64}                                    // Slope of linear fit of current stock price for a period (7 or 30 days)
                    "volatility":  dict{str : float64}                               // Volatility of current stock price for a period (7 or 30 days)
            },
            "low":
                {
                    "avg_daily_return":  dict{str : float64}                         // Average daily return of current stock price for a period (7 or 30 days)
                    "trend":  dict{str : float64}                                    // Slope of linear fit of current stock price for a period (7 or 30 days)
                    "volatility":  dict{str : float64}                               // Volatility of current stock price for a period (7 or 30 days)
            },
            "open":
                {
                    "avg_daily_return":  dict{str : float64}                         // Average daily return of current stock price for a period (7 or 30 days)
                    "trend":  dict{str : float64}                                    // Slope of linear fit of current stock price for a period (7 or 30 days)
                    "volatility":  dict{str : float64}                               // Volatility of current stock price for a period (7 or 30 days)
            },
            "volume":
                {
                    "avg":  dict{str : float64}                                      // Average of current stock volume for a period (7 or 30 days)
                    "volatility":  dict{str : float64}                               // Volatility of current stock volume for a period (7 or 30 days)
            }
        }
3. Get all-time raw data for stock
    path: GET http://127.0.0.1:5000/get/{symbol}
    params: -
    request body: -
    response body:
        {
            [
                {
                    "close": float64,                                                // Close price on the given day ("date")
                    "date": str,                                                     // Date the price data belongs to
                    "high": float64,                                                 // High price on the given day ("date")
                    "low": float64,                                                  // Low price on the given day ("date")
                    "open": float64,                                                 // Open price on the given day ("date")
                    "volume": float64                                                // Volume on the given day ("date")
                },
            ]
        }

## Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt