"""Kite chain client — native KITE transfers + data attestations (no contract required)."""
import os
import uuid
from web3 import Web3
from typing import Optional
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"


class KiteClient:
    def __init__(self):
        self.rpc_url     = os.getenv("KITE_RPC_URL", "https://rpc-testnet.gokite.ai")
        self.private_key = os.getenv("KITE_PRIVATE_KEY")

        if DEMO_MODE:
            return

        if not self.private_key:
            raise ValueError("KITE_PRIVATE_KEY is required when DEMO_MODE=false")

        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError(f"Cannot connect to Kite chain at {self.rpc_url}")

        self.account = self.w3.eth.account.from_key(self.private_key)

    def _send_tx(self, to: str, value: int = 0, data: bytes = b"") -> str:
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        try:
            chain_id = self.w3.eth.chain_id
        except Exception:
            chain_id = 2368  # KiteAI testnet

        tx = {
            "from":     self.account.address,
            "to":       self.w3.to_checksum_address(to),
            "value":    value,
            "nonce":    nonce,
            "gas":      100000,
            "gasPrice": self.w3.eth.gas_price,
            "chainId":  chain_id,
            "data":     data,
        }

        signed = self.account.sign_transaction(tx)
        raw = getattr(signed, "raw_transaction", None) or signed.rawTransaction
        tx_hash = self.w3.eth.send_raw_transaction(raw)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        if receipt.status == 0:
            raise ValueError("Transaction reverted")
        return self.w3.to_hex(tx_hash)

    def send_payment(self, to: str, amount_wei: int) -> str:
        """Send native KITE from agent wallet to recipient."""
        if DEMO_MODE:
            return "0x" + uuid.uuid4().hex + uuid.uuid4().hex[:24]

        # Cap minimum to avoid 0-value payments; ensure non-zero for demo
        if amount_wei <= 0:
            amount_wei = 1  # 1 wei sentinel

        try:
            return self._send_tx(to=to, value=amount_wei, data=b"")
        except Exception as e:
            raise Exception(f"Payment failed: {e}")

    def post_attestation(self, data_hash: str) -> str:
        """Post attestation by sending a 0-value self-tx with the hash in calldata."""
        if DEMO_MODE:
            return "0x" + uuid.uuid4().hex + uuid.uuid4().hex[:24]

        try:
            if not data_hash.startswith("0x"):
                data_hash = "0x" + data_hash
            data_bytes = self.w3.to_bytes(hexstr=data_hash)
            # Self-tx with attestation hash encoded in calldata — on-chain proof
            return self._send_tx(to=self.account.address, value=0, data=data_bytes)
        except Exception as e:
            raise Exception(f"Attestation failed: {e}")

    def get_balance(self, address: Optional[str] = None) -> int:
        if DEMO_MODE:
            return 0
        addr = self.w3.to_checksum_address(address or self.account.address)
        return self.w3.eth.get_balance(addr)
