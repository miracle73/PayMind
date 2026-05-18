"""Kite chain client integration using web3.py."""
import os
import uuid
from web3 import Web3
from typing import Optional
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"


class KiteClient:
    def __init__(self):
        self.rpc_url         = os.getenv("KITE_RPC_URL")
        self.private_key     = os.getenv("KITE_PRIVATE_KEY")
        self.contract_address = os.getenv("KITE_CONTRACT_ADDRESS")

        if DEMO_MODE:
            return  # skip chain connection in demo mode

        if not all([self.rpc_url, self.private_key, self.contract_address]):
            raise ValueError("Missing: KITE_RPC_URL, KITE_PRIVATE_KEY, KITE_CONTRACT_ADDRESS")

        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError(f"Cannot connect to Kite chain at {self.rpc_url}")

        self.account = self.w3.eth.account.from_key(self.private_key)
        self.contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(self.contract_address),
            abi=self._get_contract_abi(),
        )

    def _get_contract_abi(self) -> list:
        return [
            {
                "inputs": [{"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}],
                "name": "sendPayment",
                "outputs": [{"name": "", "type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function",
            },
            {
                "inputs": [{"name": "dataHash", "type": "bytes32"}],
                "name": "postAttestation",
                "outputs": [{"name": "", "type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function",
            },
        ]

    def send_payment(self, to: str, amount_wei: int) -> str:
        if DEMO_MODE:
            return "0x" + uuid.uuid4().hex + uuid.uuid4().hex[:24]

        try:
            to_checksum = self.w3.to_checksum_address(to)
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            tx = self.contract.functions.sendPayment(to_checksum, amount_wei).build_transaction({
                "from": self.account.address,
                "nonce": nonce,
                "gas": 300000,
                "gasPrice": self.w3.eth.gas_price,
            })
            signed = self.account.sign_transaction(tx)
            raw = getattr(signed, "raw_transaction", None) or signed.rawTransaction
            tx_hash = self.w3.eth.send_raw_transaction(raw)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt.status == 0:
                raise ValueError("Payment transaction reverted")
            return self.w3.to_hex(tx_hash)
        except Exception as e:
            raise Exception(f"Payment failed: {e}")

    def post_attestation(self, data_hash: str) -> str:
        if DEMO_MODE:
            return "0x" + uuid.uuid4().hex + uuid.uuid4().hex[:24]

        try:
            if not data_hash.startswith("0x"):
                data_hash = "0x" + data_hash
            bytes32_hash = self.w3.to_bytes(hexstr=data_hash)
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            tx = self.contract.functions.postAttestation(bytes32_hash).build_transaction({
                "from": self.account.address,
                "nonce": nonce,
                "gas": 200000,
                "gasPrice": self.w3.eth.gas_price,
            })
            signed = self.account.sign_transaction(tx)
            raw = getattr(signed, "raw_transaction", None) or signed.rawTransaction
            tx_hash = self.w3.eth.send_raw_transaction(raw)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt.status == 0:
                raise ValueError("Attestation transaction reverted")
            return self.w3.to_hex(tx_hash)
        except Exception as e:
            raise Exception(f"Attestation failed: {e}")

    def get_balance(self, address: Optional[str] = None) -> int:
        if DEMO_MODE:
            return 0
        addr = self.w3.to_checksum_address(address or self.account.address)
        return self.w3.eth.get_balance(addr)
