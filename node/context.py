from .toolbox import bytes_leading_zero

AUTO_BLOCK_GEN = False
TXS_PER_BLOCK = 10

DIFFICULTY_TARGET = bytes_leading_zero(bytes_len = 256//8, n_zero_bits = 24)
