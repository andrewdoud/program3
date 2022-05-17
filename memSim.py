from audioop import add
import sys

PAGE_SIZE = 256
TLB = [None] * 16
TLB_size = 0

# offset + page_num -> read 256 bytes

def fifo(addresses):
    faults = 0
    fault_rate = 0
    hits = 0
    misses = 0
    hit_rate = 0
    for addr in addresses:
        p = addr // PAGE_SIZE
        d = addr % PAGE_SIZE
        print(p, d)
    return faults, fault_rate, hits, misses, hit_rate

def lru(addresses):
    faults = 0
    fault_rate = 0
    hits = 0
    misses = 0
    hit_rate = 0
    return faults, fault_rate, hits, misses, hit_rate

def opt(addresses):
    faults = 0
    fault_rate = 0
    hits = 0
    misses = 0
    hit_rate = 0
    return faults, fault_rate, hits, misses, hit_rate

def get_addresses(ref_seq_filename):
    ref_seq_file = open(ref_seq_filename, 'r')
    lines = ref_seq_file.readlines()
    addresses = []
    for line in lines:
        address = int(line.strip())
        addresses.append(address)
    return addresses

def main(argv):
    ref_seq_filename = argv[1]
    algo = argv[2]
    num_frames = argv[3]

    addresses = get_addresses(ref_seq_filename)
    
    if algo == 'FIFO':
        page_faults, page_fault_rate, tlb_hits, tlb_misses, tlb_hit_rate = fifo(addresses)
    elif algo == 'LRU':
        page_faults, page_fault_rate, tlb_hits, tlb_misses, tlb_hit_rate = lru(addresses)
    elif algo == 'OPT':
        page_faults, page_fault_rate, tlb_hits, tlb_misses, tlb_hit_rate = opt(addresses)
    else:
        raise(ValueError(f'Invalid algorithm: {algo}'))
    
    print(f'Number of Translated Addresses = {len(addresses)}')
    print(f'Page Faults = {page_faults}')
    print(f'Page Fault Rate = {page_fault_rate}')
    print(f'TLB Hits = {tlb_hits}')
    print(f'TLB Misses = {tlb_misses}')
    print(f'TLB Hit Rate = {tlb_hit_rate}')

if __name__ == '__main__':
    main(sys.argv)
