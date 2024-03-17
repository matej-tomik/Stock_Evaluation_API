# Stock Evaluation API

## Description
This API provides a convenient method for evaluating stocks based on their ticker symbols. Simply input a single ticker, and it returns the evaluation results. Moreover, it supports batch processing for multiple tickers, returning a dictionary with successful evaluation results and any failed attempts.

## Features
- **Single Ticker Evaluation:** Input a single ticker symbol and receive evaluation results.
- **Batch Processing:** Evaluate multiple tickers at once, receiving a dictionary with both successful and failed evaluation results.

## Usage
To use the API, follow these steps:
1. Clone the repository to your local machine.
2. Set up your environment according to the provided instructions.
3. Start the API server.
4. Make requests to the API endpoints for single ticker evaluation or batch processing.
5. Receive evaluation results in the desired format.

## API Endpoints
- **Single Ticker Evaluation:** `/ticker/{ticker}`
  ### Response Syntax
  ```JSON
  {
  "graham_num": 26.35,
  "graham": 79.08,
  "dcf_advance": 72.63,
  "ddm_advance": 50.67,
  "dcf": 70.74,
  "ddm": 77.41,
  "ticker": "AAPL"
  }
  ```
- **Batch Processing:** `/tickers`
  ### Response Syntax
  ```JSON
  {
    "results": {
      "AAPL": {
        "graham_num": 26.35,
        "graham": 79.08,
        "dcf_advance": 72.63,
        "ddm_advance": 50.67,
        "dcf": 70.74,
        "ddm": 77.41,
        "ticker": "AAPL"
      }
    },
    "failed": {
      "GOOGL": {
        "graham_num": 54.48,
        "graham": 71.22,
        "dcf_advance": 71.83,
        "ddm_advance": "N/A",
        "dcf": 70.98,
        "ddm": "N/A",
        "ticker": "GOOGL"
      }
    }
  }
  ```
## Installation
To start Redis Stack server, run the following command:
```bash
docker run -d --name redis -p 6379:6379 -p 8001:8001 redis/redis-stack-server:latest
```
Then, to connect to the server using redis-cli, execute:
```
docker exec -it redis redis-cli
```
## License
This project is licensed under the [MIT License](https://opensource.org/license/mit)).

## Contact
For any inquiries or support, please contact [Matěj Tomík](mailto:mtomik.work@gmail.com).

<br />
<br />
<br />
<br />
<br />

# Stock Analysis Tool(Submodule)

## Application Description
Our application provides simplified stock analysis using three popular valuation models: Discounted Cash Flow (DCF), Dividend Discount Model (DDM), and Graham Number/Model.

### Features:
1. **DCF Analysis:** Estimate the intrinsic value of a stock based on projected future cash flows. Input key financial metrics and growth assumptions, and the DCF model calculates a fair value estimate.
2. **DDM Analysis:** Evaluate a stock's worth based on expected future dividend payments. Input dividend yield, growth rate, and discount rate to obtain a valuation.
3. **Graham Number:** Assess whether a stock is undervalued based on earnings per share (EPS) and book value per share (BVPS), named after renowned investor Benjamin Graham.
[More](https://github.com/matej-tomik/stock_screen_analyser/blob/main/README.md)
