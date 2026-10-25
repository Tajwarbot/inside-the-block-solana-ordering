from solders.hash import Hash
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

from obp.txbuild import MEMO_PROGRAM, build_memo_tx, build_transfer_tx


def test_memo_tx_compiles_to_three_instructions():
    payer = Keypair()
    tx = build_memo_tx(payer, str(Hash.default()), "o1.2", 21_000, 1_000)
    assert isinstance(tx, VersionedTransaction)
    assert len(tx.message.instructions) == 3
    assert len(tx.signatures) == 1
    assert tx.message.account_keys[0] == payer.pubkey()
    assert tx.message.header.num_required_signatures == 1
    assert tx.message.is_signer(0)
    assert tx.message.is_maybe_writable(0)  # fee payer is write-locked/writable
    program_ids = [tx.message.account_keys[ix.program_id_index] for ix in tx.message.instructions]
    assert MEMO_PROGRAM in program_ids


def test_transfer_tx_compiles_and_signs_with_payer():
    payer, recipient = Keypair(), Keypair()
    tx = build_transfer_tx(payer, recipient.pubkey(), 1_000, str(Hash.default()))
    assert len(tx.message.instructions) == 1
    assert tx.message.account_keys[0] == payer.pubkey()
    assert recipient.pubkey() in tx.message.account_keys
