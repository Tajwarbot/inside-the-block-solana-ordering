"""Build tagged memo transactions with a priority fee, plus our own-payer funding transfer.
Nothing here sends anything."""
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
from solders.hash import Hash
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.system_program import TransferParams, transfer

MEMO_PROGRAM = Pubkey.from_string("MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr")  # SPL Memo v2


def memo_tag(run, burst, seq, cu_price, send_order):
    # Kept SHORT and intentionally NON-UNIQUE: SPL Memo costs ~14.6k CU + ~380 CU per byte
    # (measured with simulateTransaction on mainnet, 2026-10-25), and the priority fee is charged
    # on the CU *limit*. Tags can repeat across runs; the transaction signature is the unique key.
    # Full metadata (run, fee, send order) lives in sent.csv keyed by signature.
    return f"o{burst}.{seq}"


def build_memo_tx(payer: Keypair, blockhash: str, memo: str, cu_limit: int, cu_price_micro: int):
    ixs = [set_compute_unit_limit(cu_limit), set_compute_unit_price(cu_price_micro),
           Instruction(MEMO_PROGRAM, memo.encode(), [AccountMeta(payer.pubkey(), True, False)])]
    msg = MessageV0.try_compile(payer.pubkey(), ixs, [], Hash.from_string(blockhash))
    return VersionedTransaction(msg, [payer])


def build_transfer_tx(payer: Keypair, recipient: Pubkey, lamports: int, blockhash: str):
    """System transfer from our payer to another one of our payer keys (funding only)."""
    ix = transfer(TransferParams(from_pubkey=payer.pubkey(), to_pubkey=recipient, lamports=lamports))
    msg = MessageV0.try_compile(payer.pubkey(), [ix], [], Hash.from_string(blockhash))
    return VersionedTransaction(msg, [payer])
