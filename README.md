# Backtrader with Real-Time Binance Integration and R Estimators

![Backtrader Logo](https://www.google.com/url?sa=i&url=https%3A%2F%2Fpixabay.com%2Fvectors%2Fbitcoin-icon-bitcoin-logo-currency-6219383%2F&psig=AOvVaw2rPC44ha0qZSEUws-wOfSo&ust=1692756484434000&source=images&cd=vfe&opi=89978449&ved=0CBAQjRxqFwoTCOifh7uX74ADFQAAAAAdAAAAABAE)

## Overview

This repository contains a modified version of the Backtrader trading framework, enhanced to enable real-time trading on the Binance exchange and facilitate communication with R for the integration of advanced estimators. Backtrader is a popular Python library for backtesting and live trading of financial strategies. This project extends its capabilities by incorporating real-time data from Binance and providing a seamless connection to R for utilizing custom estimators.

## Features

1. **Real-Time Binance Integration:** The original Backtrader library primarily focused on historical data analysis. In this version, we've integrated real-time data streaming from the Binance exchange, allowing traders to execute strategies using up-to-the-minute information.

2. **R Estimators Integration:** With the introduction of R integration, users can now utilize the power of R's statistical and machine learning capabilities for advanced strategy development. The communication channel between R and Backtrader enables seamless exchange of data and results.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/backtrader-binance-r.git
   cd backtrader-binance-r
   ```

2. Set up a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Install R packages (assuming you have R installed):
   ```R
   install.packages("Rpackages")  # Replace with required R packages
   ```

## Usage

1. **Binance API Setup:** Before running any strategy, make sure to set up your Binance API credentials in the `config.py` file.

2. **Strategy Development:** Develop your trading strategy by subclassing the provided `BacktraderRStrategy` class. This class enables interaction with R estimators and receives real-time Binance data.

3. **R Estimators:** Create R scripts in the `r_estimators` directory. Use the provided communication channel to send and receive data between Python and R. Ensure that the required R packages are installed.




## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Disclaimer: This project is developed for educational and research purposes. Trading and investing involve significant risks, and the use of this software does not guarantee any profits. Please conduct thorough testing and research before deploying any trading strategy.*
