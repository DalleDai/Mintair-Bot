# 🛠️ Mintair BOT [KITE AI, PHAROS, RISE]

Automation bot for interacting with Mintair smart contracts. Supports multi-account deployment, proxy rotation, and contract actions across EVM wallets.

---

## 🔗 Registration Steps

Before running the bot:

- Register at: https://contracts.mintair.xyz/  
- Sign with a new EVM wallet  
- Connect your Twitter account  

---

## ✨ Features

- 🔍 Auto Get Account Information  
- 🌐 Auto Run With Proxy — `Choose 1`  
- 🚫 Auto Run Without Proxy — `Choose 2`  
- 🔁 Auto Rotate Invalid Proxies — `y` or `n`  
- ⏱️ Auto Perform Timer Deploy Contract  
- 💰 Auto Perform Token Deploy Contract  
- 🖼️ Auto Perform NFT Deploy Contract  
- 👥 Multi-Account Support  

---

## 🌍 Proxy Recommendation

For multi-wallet automation, airdrop farming, or bypassing geo-restrictions:

🔗 https://www.nstproxy.com/?utm_source=YETIDAO  
👉 Use code **YETIDAO** for **10% OFF**

- From $0.1/GB  
- Global coverage  
- Rotation control  
- Anti-ban tech  

---

## 🧰 Requirements

- Python 3.9 or higher  
- pip (Python package manager)

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/DalleDai/Mintair-Bot.git
cd Mintair-Bot
```

### 2. Set Up Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🧪 Library Version Check (Optional)

If you encounter errors, check your `web3` and `eth-account` versions:

- Check version:

```bash
pip show library_name
```

- Uninstall:

```bash
pip uninstall library_name
```

- Reinstall with correct version:

```bash
pip install library_name==version
```

---

## 📝 Configuration

### accounts.txt

Add your private keys, one per line:

```
your_private_key_1
your_private_key_2
```

### proxy.txt

Supported formats:

```
ip:port                     # Default protocol: HTTP
protocol://ip:port
protocol://user:pass@ip:port
```

---

## ▶️ Run the Bot

```bash
python bot.py
# or
python3 bot.py
```

---

## ☕ Buy Me a Coffee

- EVM: `0x3b94Ff1611773171E06047C0041099CccCFC609F`

---

## 🙌 Contribute & Connect

Thanks for visiting this repository!  
If you find it useful, please ⭐ star and follow.  
For questions, issues, or suggestions, feel free to open an issue or reach out.

---

