"""Kite chain client integration using web3.py."""
import os
from web3 import Web3
from web3.exceptions import TransactionNotFound
from typing import Optional


class KiteClient:
    """Client for interacting with Kite chain (EVM-compatible)."""

    def __init__(self):
        """Initialize Kite client with environment configuration."""
        self.rpc_url = os.getenv("KITE_RPC_URL")
        self.private_key = os.getenv("KITE_PRIVATE_KEY")
        self.contract_address = os.getenv("KITE_CONTRACT_ADDRESS")

        if not all([self.rpc_url, self.private_key, self.contract_address]):
            raise ValueError("Missing required environment variables: KITE_RPC_URL, KITE_PRIVATE_KEY, KITE_CONTRACT_ADDRESS")

        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))

        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to Kite chain at {self.rpc_url}")

        # Set up account from private key
        self.account = self.w3.eth.account.from_key(self.private_key)

        # Load contract ABI (minimal for transfer and attestation)
        # In production, load from actual contract ABI file
        self.contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(self.contract_address),
            abi=self._get_contract_abi()
        )

    def _get_contract_abi(self) -> list:
        """
        Return minimal contract ABI for payment and attestation.
        In production, this should be loaded from a compiled JSON file.
        """
        return [
            {
                "inputs": [
                    {"name": "to", "type": "address"},
                    {"name": "amount", "type": "uint256"}
                ],
                "name": "sendPayment",
                "outputs": [{"name": "", "type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "dataHash", "type": "bytes32"}
                ],
                "name": "postAttestation",
                "outputs": [{"name": "", "type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": False, "name": "from", "type": "address"},
                    {"indexed": False, "name": "to", "type": "address"},
                    {"indexed": False, "name": "amount", "type": "uint256"}
                ],
                "name": "PaymentSent",
                "type": "event"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": False, "name": "attester", "type": "address"},
                    {"indexed": False, "name": "dataHash", "type": "bytes32"}
                ],
                "name": "AttestationPosted",
                "type": "event"
            }
        ]

    def send_payment(self, to: str, amount_wei: int) -> str:
        """
        Send payment to recipient on Kite chain.

        Args:
            to: Recipient address (checksum)
            amount_wei: Amount in wei

        Returns:
            Transaction hash as hex string
        """
        try:
            to_checksum = self.w3.to_checksum_address(to)

            # Get nonce
            nonce = self.w3.eth.get_transaction_count(self.account.address)

            # Build transaction
            tx = self.contract.functions.sendPayment(to_checksum, amount_wei).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 300000,  # Gas limit
                'gasPrice': self.w3.eth.gas_price,
            })

            # Sign transaction
            signed_tx = self.account.sign_transaction(tx)

            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            # Wait for receipt (optional, can be async in production)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt.status == 0:
                raise ValueError("Transaction failed: receipt status 0")

            return self.w3.to_hex(tx_hash)

        except Exception as e:
            raise Exception(f"Payment failed: {str(e)}")

    def post_attestation(self, data_hash: str) -> str:
        """
        Post attestation on Kite chain.

        Args:
            data_hash: SHA256 hash of attestation data (hex string, 0x prefixed)

        Returns:
            Transaction hash as hex string
        """
        try:
            # Ensure data_hash is bytes32
            if not data_hash.startswith("0x"):
                data_hash = "0x" + data_hash
            bytes32_hash = self.w3.to_bytes(hexstr=data_hash)

            # Get nonce
            nonce = self.w3.eth.get_transaction_count(self.account.address)

            # Build transaction
            tx = self.contract.functions.postAttestation(bytes32_hash).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
            })

            # Sign transaction
            signed_tx = self.account.sign_transaction(tx)

            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt.status == 0:
                raise ValueError("Attestation transaction failed")

            return self.w3.to_hex(tx_hash)

        except Exception as e:
            raise Exception(f"Attestation failed: {str(e)}")

    def get_balance(self, address: Optional[str] = None) -> int:
        """Get balance in wei for an address."""
        addr = self.w3.to_checksum_address(address or self.account.address)
        return self.w3.eth.get_balance(addr)
