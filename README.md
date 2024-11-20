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

### 1. Collect Stock Data
**Path**:  
`POST http://127.0.0.1:5000/collect`

**Params**:  
None.

**Request Body**:  
```json
{
    "symbols": ["str"]  // List of stock symbols to download from the Yahoo Finance API
}
```
### 2. Analyze stock data
 **Path**:  
`GET http://127.0.0.1:5000/analyze/{symbol}`

**Params**:  
None.

**Request Body**:
None.

**Response Body**:
```json
{   // Within each price type or volume, all values are calculated for a period of 7 days (5 workdays) or 30 days
    "close":
        {   
            "TOP_STOCK"+"_correlation_coeff": dict{str : float64}  //Pearson corr. coeff.
            "avg_daily_return": dict{str : float64}  // Avg daily return of current price
            "risk_reward_ratio": dict{str : float64}  // RRO of current price
            "total_return": dict{str : float64}  // Total return of current price
            "trend": dict{str : float64}  // Slope of linear fit for current price
            "volatility": dict{str : float64}  // Volatility of current price
    },
    "high":
        {
            "avg_daily_return": dict{str : float64}  // Avg daily return of current price
            "trend": dict{str : float64}  // Slope of linear fit for current price
            "volatility": dict{str : float64}  // Volatility of current price
    },
    "low":
        {
            "avg_daily_return": dict{str : float64}  // Avg daily return of current price
            "trend": dict{str : float64}  // Slope of linear fit for current price
            "volatility": dict{str : float64}  // Volatility of current price
    },
    "open":
        {
            "avg_daily_return": dict{str : float64}  // Avg daily return of current price
            "trend": dict{str : float64}  // Slope of linear fit for current price
            "volatility": dict{str : float64}  // Volatility of current price
    },
    "volume":
        {
            "avg": dict{str : float64}  // Average of current stock volume
            "volatility": dict{str : float64}  // Volatility of stock volume
    }
}
```
    
### 3. Get all-time raw data for stock
 **Path**: 
 `GET http://127.0.0.1:5000/get/{symbol}`

**Params**:  
None.

**Request Body**:
None.

**Response Body**:
```json
{
    [
        {
            "close": float64,              // Close price on the given day ("date")
            "date": str,                   // Date the price data belongs to
            "high": float64,               // High price on the given day ("date")
            "low": float64,                // Low price on the given day ("date")
            "open": float64,               // Open price on the given day ("date")
            "volume": float64              // Volume on the given day ("date")
        },
    ]
}
```

## Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt