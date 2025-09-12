from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, BasicAuth
from aiohttp_socks import ProxyConnector
from datetime import datetime
from colorama import *
import asyncio, random, re, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Giwa:
    def __init__(self) -> None:
        self.L1_NETWORK = {
            "name": "Sepolia ETH",
            "rpc_url": "https://ethereum-sepolia-rpc.publicnode.com",
            "explorer": "https://sepolia.etherscan.io/tx/",
            "contract": "0x956962C34687A954e611A83619ABaA37Ce6bC78A",
            "abi": [
                {
                    "type": "function",
                    "name": "depositTransaction",
                    "stateMutability": "payable",
                    "inputs": [
                        { "internalType": "address", "name": "_to", "type": "address" },
                        { "internalType": "uint256", "name": "_value", "type": "uint256" },
                        { "internalType": "uint64", "name": "_gasLimit", "type": "uint64" },
                        { "internalType": "bool", "name": "_isCreation", "type": "bool" },
                        { "internalType": "bytes", "name": "_data", "type": "bytes" }
                    ],
                    "outputs": []
                }
            ]
        }
        self.L2_NETWORK = {
            "name": "Giwa Sepolia",
            "rpc_url": "https://sepolia-rpc.giwa.io",
            "explorer": "https://sepolia-explorer.giwa.io/tx/",
            "contract": "0x4200000000000000000000000000000000000016",
            "abi": [
                {
                    "type": "function",
                    "name": "initiateWithdrawal",
                    "stateMutability": "payable",
                    "inputs": [
                        { "internalType": "address", "name": "_target", "type": "address" },
                        { "internalType": "uint256", "name": "_gasLimit", "type": "uint256" },
                        { "internalType": "bytes", "name": "_data", "type": "bytes" }
                    ],
                    "outputs": []
                }
            ]
        }
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.bridge_count = 0
        self.bridge_amount = 0
        self.min_delay = 0
        self.max_delay = 0

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self, project_name="GiwaTestnet"):
        border = "═" * 58  # Solid elite border
        print(Fore.LIGHTBLUE_EX + Style.BRIGHT + border)
        print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "    👑 YetiDAO PRIME Automation BOT 👑")
        print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + "    ─────────────────────────────────────")
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + f"   🧠 Project    :  GiwaTestnet - PRIME Bot")
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "    💻 Author     : YetiDAO")
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "    🌐 Status     : Active & Privately Monitored 🔒")
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "    🚀 Mode       : PRIME Access (VIP Only)")
        print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + "    ─────────────────────────────────────")
        print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "    💎 Powered by Cryptodai3 × YetiDAO | Prime Engine v1.0 ⚙️")
        print(Fore.LIGHTBLUE_EX + Style.BRIGHT + border)

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self):
        filename = "proxy.txt"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                return
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def build_proxy_config(self, proxy=None):
        if not proxy:
            return None, None, None

        if proxy.startswith("socks"):
            connector = ProxyConnector.from_url(proxy)
            return connector, None, None

        elif proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", proxy)
            if match:
                username, password, host_port = match.groups()
                clean_url = f"http://{host_port}"
                auth = BasicAuth(username, password)
                return None, clean_url, auth
            else:
                return None, proxy, None

        raise Exception("Unsupported Proxy Type.")
    
    def generate_address(self, account: str):
        try:
            account = Account.from_key(account)
            address = account.address
            
            return address
        except Exception as e:
            return None
        
    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account
        except Exception as e:
            return None
        
    async def get_web3_with_check(self, address: str, network: dict, use_proxy: bool, retries=3, timeout=60):
        request_kwargs = {"timeout": timeout}

        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        if use_proxy and proxy:
            request_kwargs["proxies"] = {"http": proxy, "https": proxy}

        for attempt in range(retries):
            try:
                web3 = Web3(Web3.HTTPProvider(network["rpc_url"], request_kwargs=request_kwargs))
                web3.eth.get_block_number()
                return web3
            except Exception as e:
                if attempt < retries:
                    await asyncio.sleep(3)
                    continue
                raise Exception(f"Failed to Connect to RPC: {str(e)}")
        
    async def get_token_balance(self, address: str, network: dict, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, network, use_proxy)

            balance = web3.eth.get_balance(address)
            token_balance = balance / (10**18)

            return token_balance
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
        
    async def send_raw_transaction_with_retries(self, account, web3, tx, retries=5):
        for attempt in range(retries):
            try:
                signed_tx = web3.eth.account.sign_transaction(tx, account)
                raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_hash = web3.to_hex(raw_tx)
                return tx_hash
            except TransactionNotFound:
                pass
            except Exception as e:
                pass
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Hash Not Found After Maximum Retries")

    async def wait_for_receipt_with_retries(self, web3, tx_hash, retries=5):
        for attempt in range(retries):
            try:
                receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
                return receipt
            except TransactionNotFound:
                pass
            except Exception as e:
                pass
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Receipt Not Found After Maximum Retries")
    
    async def perform_deposit(self, account: str, address: str, network: dict, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, network, use_proxy)

            amount_to_wei = web3.to_wei(self.bridge_amount, "ether")

            token_contract = web3.eth.contract(address=web3.to_checksum_address(network["contract"]), abi=network["abi"])
            deposit_data = token_contract.functions.depositTransaction(address, amount_to_wei, 21000, False, b'')

            estimated_gas = deposit_data.estimate_gas({"from":address, "value":amount_to_wei})
            max_priority_fee = web3.to_wei(0.001, "gwei")
            max_fee = max_priority_fee

            deposit_tx = deposit_data.build_transaction({
                "from": address,
                "value": amount_to_wei,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, deposit_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            block_number = receipt.blockNumber

            return tx_hash, block_number

        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
    
    async def perform_withdraw(self, account: str, address: str, network: dict, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, network, use_proxy)

            amount_to_wei = web3.to_wei(self.bridge_amount, "ether")

            token_contract = web3.eth.contract(address=web3.to_checksum_address(network["contract"]), abi=network["abi"])
            withdraw_data = token_contract.functions.initiateWithdrawal(address, 21000, b'')

            estimated_gas = withdraw_data.estimate_gas({"from":address, "value":amount_to_wei})
            max_priority_fee = web3.to_wei(0.001, "gwei")
            max_fee = max_priority_fee

            withdraw_tx = withdraw_data.build_transaction({
                "from": address,
                "value": amount_to_wei,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, withdraw_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            block_number = receipt.blockNumber

            return tx_hash, block_number

        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def print_timer(self):
        for remaining in range(random.randint(self.min_delay, self.max_delay), 0, -1):
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {remaining} {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Seconds For Next Tx...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)

    def print_bridge_question(self):
        while True:
            try:
                bridge_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}Bridge Count -> {Style.RESET_ALL}").strip())
                if bridge_count > 0:
                    self.bridge_count = bridge_count
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter positive number.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                bridge_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter ETH Amount -> {Style.RESET_ALL}").strip())
                if bridge_amount > 0:
                    self.bridge_amount = bridge_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

    def print_delay_question(self):
        while True:
            try:
                min_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Min Delay For Each Tx -> {Style.RESET_ALL}").strip())
                if min_delay >= 0:
                    self.min_delay = min_delay
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Min Delay must be >= 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                max_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Max Delay For Each Tx -> {Style.RESET_ALL}").strip())
                if max_delay >= min_delay:
                    self.max_delay = max_delay
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Max Delay must be >= Min Delay.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

    def print_question(self):
        while True:
            try:
                print(f"{Fore.GREEN + Style.BRIGHT}Select Option:{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}1. Bridge Sepolia to Giwa{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Bridge Giwa to Sepolia{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Random Bridge{Style.RESET_ALL}")
                option = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if option in [1, 2, 3]:
                    option_type = (
                        "Bridge Sepolia to Giwa" if option == 1 else 
                        "Bridge Giwa to Sepolia" if option == 2 else 
                        "Random Bridge"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{option_type} Selected.{Style.RESET_ALL}")

                    self.print_bridge_question()
                    self.print_delay_question()
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2, or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2, or 3).{Style.RESET_ALL}")

        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run Without Proxy{Style.RESET_ALL}")
                proxy_choice = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())

                if proxy_choice in [1, 2]:
                    proxy_type = "With" if proxy_choice == 1 else "Without"
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")

        rotate_proxy = False
        if proxy_choice == 1:
            while True:
                rotate_proxy = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate_proxy in ["y", "n"]:
                    rotate_proxy = rotate_proxy == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return option, proxy_choice, rotate_proxy
    
    async def check_connection(self, proxy_url=None):
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get(url="https://api.ipify.org?format=json", proxy=proxy, proxy_auth=proxy_auth, ssl=False) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError) as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Connection Not 200 OK {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
        
        return None
    
    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy)
            if not is_valid:
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(address)
                    await asyncio.sleep(1)
                    continue

                return False

            return True
        
    async def process_perform_deposit(self, account: str, address: str, network: dict, use_proxy: bool):
        tx_hash, block_number = await self.perform_deposit(account, address, network, use_proxy)
        if tx_hash and block_number:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {network['explorer']}{tx_hash} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )
        
    async def process_perform_withdraw(self, account: str, address: str, network: dict, use_proxy: bool):
        tx_hash, block_number = await self.perform_withdraw(account, address, network, use_proxy)
        if tx_hash and block_number:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {network['explorer']}{tx_hash} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )
        
    async def process_option_1(self, account: str, address: str, use_proxy: bool):
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}     Pair    :{Style.RESET_ALL}"
            f"{Fore.BLUE+Style.BRIGHT} Sepolia to Giwa {Style.RESET_ALL}"
        )
        
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}     Amount  :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {self.bridge_amount} ETH {Style.RESET_ALL}"
        )

        balance = await self.get_token_balance(address, self.L1_NETWORK, use_proxy)
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}     Balance :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {balance} ETH {Style.RESET_ALL}"
        )

        if balance is None:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Fetch ETH Token Balance Failed {Style.RESET_ALL}"
            )
            return

        if balance <= self.bridge_amount:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} Insufficient ETH Token Balance {Style.RESET_ALL}"
            )
            return

        await self.process_perform_deposit(account, address, self.L1_NETWORK, use_proxy)
        
    async def process_option_2(self, account: str, address: str, use_proxy: bool):
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}     Pair    :{Style.RESET_ALL}"
            f"{Fore.BLUE+Style.BRIGHT} Giwa to Sepolia {Style.RESET_ALL}"
        )

        self.log(
            f"{Fore.CYAN+Style.BRIGHT}     Amount  :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {self.bridge_amount} ETH {Style.RESET_ALL}"
        )

        balance = await self.get_token_balance(address, self.L2_NETWORK, use_proxy)
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}     Balance :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {balance} ETH {Style.RESET_ALL}"
        )

        if balance is None:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Fetch ETH Token Balance Failed {Style.RESET_ALL}"
            )
            return

        if balance <= self.bridge_amount:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} Insufficient ETH Token Balance {Style.RESET_ALL}"
            )
            return

        await self.process_perform_withdraw(account, address, self.L2_NETWORK, use_proxy)

    async def process_accounts(self, account: str, address: str, option: int, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
        if is_valid:

            if option == 1:
                self.log(f"{Fore.CYAN+Style.BRIGHT}Bridge    :{Style.RESET_ALL}")
                for i in range(self.bridge_count):
                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT}{i+1}{Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT} Of {Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT}{self.bridge_count}{Style.RESET_ALL}                           "
                    )
                    await self.process_option_1(account, address, use_proxy)
                    await self.print_timer()

            elif option == 2:
                self.log(f"{Fore.CYAN+Style.BRIGHT}Bridge    :{Style.RESET_ALL}")
                for i in range(self.bridge_count):
                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT}{i+1}{Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT} Of {Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT}{self.bridge_count}{Style.RESET_ALL}                           "
                    )
                    await self.process_option_2(account, address, use_proxy)
                    await self.print_timer()

            elif option == 3:
                self.log(f"{Fore.CYAN+Style.BRIGHT}Bridge    :{Style.RESET_ALL}")
                for i in range(self.bridge_count):
                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT}{i+1}{Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT} Of {Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT}{self.bridge_count}{Style.RESET_ALL}                           "
                    )

                    bridge = random.choice([self.process_option_1, self.process_option_2])
                    await bridge(account, address, use_proxy)
                    await self.print_timer()

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            
            option, proxy_choice, rotate_proxy = self.print_question()

            while True:
                use_proxy = True if proxy_choice == 1 else False

                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies()
                
                separator = "=" * 25
                for account in accounts:
                    if account:
                        address = self.generate_address(account)
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if not address:
                            self.log(
                                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                                f"{Fore.RED+Style.BRIGHT} Invalid Private Key or Libraries Version Not Supported {Style.RESET_ALL}"
                            )
                            continue
                        
                        await self.process_accounts(account, address, option, use_proxy, rotate_proxy)
                        await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*72)
                seconds = 24 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed.{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except ( Exception, ValueError ) as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = Giwa()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Giwa Testnet - BOT{Style.RESET_ALL}                                       "                              
        )
