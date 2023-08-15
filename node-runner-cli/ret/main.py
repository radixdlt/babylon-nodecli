import logging
from secrets import token_bytes
from ret.radix_engine_toolkit_uniffi import (PrivateKey,
                                             Curve,
                                             derive_virtual_account_address_from_public_key,
                                             ManifestBuilder)

if __name__ == "__main__":
    random_bytes = token_bytes(32)
    private_key = PrivateKey(random_bytes, Curve.ED25519)
    address = derive_virtual_account_address_from_public_key(private_key.public_key(), 13)
    manifest_builder = ManifestBuilder()
    lock_fee_transaction = manifest_builder.faucet_lock_fee().build(13)
    free_xrd_transaction = manifest_builder.faucet_free_xrd().build(13)
    deposit_transaction = manifest_builder.account_deposit_batch(address).build(13)

    logging.info("PEPE")