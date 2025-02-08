# 🚀 MetaTrader 5 Trading Bot  

A Python-based trading bot for MetaTrader 5 that automates trades based on ATR-based risk management and high-confidence trade setups. The bot identifies strong trends, price rejections, and executes trades dynamically with a 1:2 risk-reward ratio.  

## 📦 Installation  

### Prerequisites  
Make sure you have the following installed:  
- Python 3.x: [Download & Install Python](https://www.python.org/downloads/)  
- MetaTrader 5: [Download & Install MetaTrader 5](https://www.metatrader5.com/en/download)  
- Required Python libraries: `MetaTrader5`, `pandas`, `numpy`  

### 🔹 Clone the Repository  
Open your terminal and run:  

```sh
git clone https://github.com/your-username/your-repo.git
```

### 🔹 Navigate to the Project Folder  
```sh
cd your-repo
```

### 🔹 Install Dependencies  
```sh
pip install -r requirements.txt
```

### 🔹 Configure Your Trading Account  
Update the following values in the script:  

```python
MT5_SERVER = 'Your-Broker-Server'
MT5_LOGIN = Your-MT5-Account-ID
MT5_PASSWORD = 'Your-Password'
SYMBOL = 'Your-Trading-Symbol'
```

### 🔹 Run the Trading Bot  
```sh
python bot.py
```

The bot will start scanning the market and placing trades based on its strategy.  

## ⚠️ Disclaimer  
Use this bot at your own risk. Ensure you test it on a demo account before deploying it in live trading.  

---
