from itertools import product

V_CELL_MAX = 4.35
V_CELL_NOM = 3.8
V_CELL_MIN = 3.0

N_STACKS = 5
N_CELLS = 14
N_NTCS = 6

RANGE_STACKS = range(1, N_STACKS+1)
RANGE_SPIS = range(2, 4)
RANGE_CELLS = range(1, N_CELLS+1)
RANGE_NTCS = range(1, N_NTCS+1)

RANGE_VBAT = product(RANGE_STACKS, RANGE_SPIS, RANGE_CELLS)
RANGE_TBAT = product(RANGE_STACKS, RANGE_SPIS, RANGE_NTCS)

SLICE_CELLS = lambda i: slice(2*N_CELLS*(i-1), 2*N_CELLS*i)
SLICE_NTCS = lambda i: slice(2*N_NTCS*(i-1), 2*N_NTCS*i)

GHOST_CELLS = [
    'Cell14_s1_spi2',
    'Cell14_s2_spi3',
    'Cell14_s3_spi2',
    'Cell14_s4_spi3',
    'Cell14_s5_spi2',
]