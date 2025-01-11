import hashlib, binascii, struct, array, os, time, sys, argparse
import scrypt
from construct import *
from construct import Struct, Int32ub, Bytes, Byte


# Entry point
def main():
    # Parse command-line arguments
    options = get_args()

    # Determine the hashing algorithm to use
    algorithm = get_algorithm(options)

    # Create the input and output scripts
    input_script = create_input_script(options.timestamp)
    output_script = create_output_script(options.pubkey)

    # Generate the hash merkle root (double SHA256 of transaction data)
    tx = create_transaction(input_script, output_script, options)
    hash_merkle_root = hashlib.sha256(hashlib.sha256(tx).digest()).digest()

    # Display genesis block details
    print_block_info(options, hash_merkle_root)

    # Build block header and start hash generation
    block_header = create_block_header(hash_merkle_root, options.time, options.bits, options.nonce)
    genesis_hash, nonce = generate_hash(block_header, algorithm, options.nonce, options.bits)

    # Announce the genesis hash when found
    announce_found_genesis(genesis_hash, nonce)

# Parse command-line arguments
def get_args():
    parser = argparse.ArgumentParser(description="Generate a genesis block for a cryptocurrency.")
    parser.add_argument("-t", "--time", dest="time", type=int, default=int(time.time()),
                        help="The (UNIX) time for genesis block creation.")
    parser.add_argument("-z", "--timestamp", dest="timestamp",
                        default="The Times 01/Jan/2025 New Year's dawn brings hope for a better future",
                        help="The pszTimestamp found in the coinbase of the genesis block.")
    parser.add_argument("-n", "--nonce", dest="nonce", type=int, default=0,
                        help="Initial nonce value for hash search.")
    parser.add_argument("-a", "--algorithm", dest="algorithm", default="SHA256",
                        choices=["SHA256", "scrypt", "X11", "X13", "X15"],
                        help="Proof-of-Work algorithm: [SHA256|scrypt|X11|X13|X15].")
    parser.add_argument("-p", "--pubkey", dest="pubkey",
                        default="04902bda9e9feaa9c7206f8eae4b3ea5f5c1d7fbf77f00971b8ddf275b74650e366a08712058fe4c76e17ea38f99bd1e4e54a451715cbb71398a584fb8c6717b16",
                        help="The pubkey found in the output script.")
    parser.add_argument("-v", "--value", dest="value", type=int, default=7000000,
                        help="Output value (e.g., 7M coins per block = 7000000).")

    parser.add_argument("-b", "--bits", dest="bits", type=int, default=0x1e0ffff0,
                        help="Target difficulty in compact representation (default: 0x1e0ffff0).")

    args = parser.parse_args()

    # Set default bits if not provided
    if not args.bits:
        if args.algorithm in ["scrypt", "X11", "X13", "X15"]:
            args.bits = 0x1f0fffff # Default for scrypt-based coins
        else:
            args.bits = 0x1e0ffff0  # Default for SHA256

    return args


# Validate and return the algorithm
def get_algorithm(options):
    supported_algorithms = ["SHA256", "scrypt", "X11", "X13", "X15"]
    if options.algorithm not in supported_algorithms:
        sys.exit(f"Error: Algorithm must be one of {supported_algorithms}")
    return options.algorithm

# Generate the input script
def create_input_script(psz_timestamp):
    psz_prefix = ""
    # Add OP_PUSHDATA1 if timestamp length exceeds 76 bytes
    if len(psz_timestamp) > 76:
        psz_prefix = '4c'

    script_prefix = '04ffff001d0104' + psz_prefix + len(psz_timestamp).to_bytes(1, 'big').hex()
    return bytes.fromhex(script_prefix + psz_timestamp.encode('utf-8').hex())

# Generate the output script
def create_output_script(pubkey):
    script_len = '41'  # Length of public key in hex
    OP_CHECKSIG = 'ac'
    return bytes.fromhex(script_len + pubkey + OP_CHECKSIG)

# Create a transaction for the genesis block
def create_transaction(input_script, output_script, options):
    transaction = Struct(
        "version" / Bytes(4),
        "num_inputs" / Byte,
        "prev_output" / Bytes(32),
        "prev_out_idx" / Int32ub,  # Correct usage of Int32ub
        "input_script_len" / Byte,
        "input_script" / Bytes(len(input_script)),
        "sequence" / Int32ub,
        "num_outputs" / Byte,
        "out_value" / Bytes(8),
        "output_script_len" / Byte,
        "output_script" / Bytes(len(output_script)),
        "locktime" / Int32ub
    )

    tx = transaction.parse(b'\x00' * (127 + len(input_script)))
    tx.version = struct.pack('<I', 1)
    tx.num_inputs = 1
    tx.prev_output = b'\x00' * 32
    tx.prev_out_idx = 0xFFFFFFFF
    tx.input_script_len = len(input_script)
    tx.input_script = input_script
    tx.sequence = 0xFFFFFFFF
    tx.num_outputs = 1
    tx.out_value = struct.pack('<q', options.value)
    tx.output_script_len = len(output_script)
    tx.output_script = output_script
    tx.locktime = 0
    return transaction.build(tx)


# Generate the block header
def create_block_header(hash_merkle_root, time, bits, nonce):
    block_header = Struct(
        "version" / Bytes(4),
        "hash_prev_block" / Bytes(32),
        "hash_merkle_root" / Bytes(32),
        "time" / Bytes(4),
        "bits" / Bytes(4),
        "nonce" / Bytes(4)
    )

    header = block_header.parse(b'\x00' * 80)
    header.version = struct.pack('<I', 1)
    header.hash_prev_block = b'\x00' * 32
    header.hash_merkle_root = hash_merkle_root
    header.time = struct.pack('<I', time)
    header.bits = struct.pack('<I', bits)
    header.nonce = struct.pack('<I', nonce)
    return block_header.build(header)

# Generate hash using the chosen algorithm
def generate_hash(data_block, algorithm, start_nonce, bits):
    print("Searching for genesis hash...")
    nonce = start_nonce
    last_updated = time.time()

    target = (bits & 0xffffff) * 2 ** (8 * ((bits >> 24) - 3))

    while True:
        sha256_hash, header_hash = generate_hashes_from_block(data_block, algorithm)
        last_updated = calculate_hashrate(nonce, last_updated)

        if is_genesis_hash(header_hash, target):
            return (header_hash if algorithm != "SHA256" else sha256_hash, nonce)

        nonce += 1
        data_block = data_block[:-4] + struct.pack('<I', nonce)

# Generate double SHA256 or algorithm-specific hash
def generate_hashes_from_block(data_block, algorithm):
    sha256_hash = hashlib.sha256(hashlib.sha256(data_block).digest()).digest()[::-1]
    if algorithm == "scrypt":
        header_hash = scrypt.hash(data_block, data_block, 1024, 1, 1, 32)[::-1]
    elif algorithm == "SHA256":
        header_hash = sha256_hash
    else:
        sys.exit(f"Unsupported algorithm: {algorithm}")
    return sha256_hash, header_hash

# Check if the hash meets the target
def is_genesis_hash(header_hash, target):
    return int(header_hash.hex(), 16) < target

# Calculate and display the hash rate
def calculate_hashrate(nonce, last_updated):
    if nonce % 1000000 == 999999:
        now = time.time()
        hashrate = round(1000000 / (now - last_updated))
        generation_time = round((2**32 / hashrate) / 3600, 1)
        sys.stdout.write(f"\r{hashrate} H/s, estimate: {generation_time} h")
        sys.stdout.flush()
        return now
    return last_updated

# Display genesis block details
def print_block_info(options, hash_merkle_root):
    print("algorithm: " + options.algorithm)
    print("merkle hash: " + hash_merkle_root[::-1].hex())
    print("pszTimestamp: " + options.timestamp)
    print("pubkey: " + options.pubkey)
    print("time: " + str(options.time))
    print("bits: " + hex(options.bits))

# Announce when genesis hash is found
def announce_found_genesis(genesis_hash, nonce):
    print("\ngenesis hash found!")
    print("nonce: " + str(nonce))
    print("genesis hash: " + genesis_hash.hex())

# Execute the main function
if __name__ == "__main__":
    main()
