import hashlib

import ecdsa
from OpenSSL.crypto import load_pkcs12
from cryptography.hazmat.primitives._serialization import Encoding, PrivateFormat, NoEncryption

from radix_engine_toolkit import (
    PrivateKey,
    Address,
    derive_virtual_account_address_from_public_key
)


def derive_address(keystore: str, password: str, network_id: int) -> Address:
    print("PEPE")
    print(keystore)
    keystore = load_pkcs12(open(keystore,"rb").read(), password)
    print(keystore)
    cryptography_key = keystore.get_privatekey().to_cryptography_key()
    print(cryptography_key)
    private_key_bytes = cryptography_key.private_bytes(
        encoding=Encoding.DER,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption())

    private_signing_key = ecdsa.SigningKey.from_der(
        private_key_bytes,
        hashfunc=hashlib.sha256)
    private_key = PrivateKey.new_secp256k1(private_signing_key.to_string())

    return derive_virtual_account_address_from_public_key(
        public_key=private_key.public_key(), network_id=network_id)