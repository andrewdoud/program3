from io import BufferedReader
import sys

PAGE_SIZE = 256

# offset + page_num -> read 256 bytes

def search_tlb(tlb, p):
    for entry in tlb:
        if entry is not None and entry[0] == p:
            return entry # (p, f)
    return False

def fifo(addresses, num_frames: int, backing_store: BufferedReader):
    faults = fault_rate = hits = misses = hit_rate = 0 # Metrics

    # init tlb
    tlb = [None] * 16
    tlb_p = 0 # tlb pointer

    # init page table
    page_table = [(None, 0)] * PAGE_SIZE # (frame_number, valid_bit)

    # init physical memory
    phys_mem = [(None, None)] * num_frames # (ref_byte, hex_data)
    next_f = 0

    # init frame -> p
    frame_p = [None] * num_frames

    for addr in addresses:
        p = addr // PAGE_SIZE # page number
        d = addr % PAGE_SIZE # page offset
        bs_num = p * PAGE_SIZE
        # Try to grab entry from tlb
        entry = search_tlb(tlb, p)
        if entry == False: # if miss
            misses += 1
            
            # Check if valid in the page table
            if page_table[p][1] == 1: # if already in physical mem
                f = page_table[p][0]
                # Retrieve from physical memory
                hex_data = phys_mem[f]
                print(f)
                print(hex_data)
                print()
                # Print all the stuff

            else: # if not in physical mem yet, replace curr frame in physical mem
                faults += 1
                f = next_f
                # Retrieve data from backing store
                backing_store.seek(bs_num, 0)
                hex_data = backing_store.read(PAGE_SIZE).hex().upper()

                # Retrieve reference bit from backing store
                backing_store.seek(bs_num + d, 0)
                ref_byte = backing_store.read(1)
                ref_byte_int = int.from_bytes(ref_byte, 'little', signed=True)

                # Print all the stuff
                print(f'{addr}, {ref_byte_int}, {f}, {hex_data}')
                
                # Update page table
                page_table[p] = (f, 1)

                # Update physical memory
                if frame_p[f] is not None: # If phys mem already has entry in curr frame
                    old_p = frame_p[0]
                    page_table[old_p] = (f, 0) # Clear the old page table entry
                frame_p[f] = p
                phys_mem[f] = (ref_byte_int, hex_data)

                # Increment the frame number (since FIFO goes to 0 if past end)
                next_f += 1
                if next_f >= num_frames:
                    next_f = 0

            # Replace tlb entry
            tlb[tlb_p] = (p, f)

            # Increment tlb pointer (goes to 0 if past end)
            tlb_p += 1
            if tlb_p >= len(tlb)-1:
                tlb_p = 0

        else: # if hit
            hits += 1
            # Find in page table
            f = entry[1]
            phys_mem[next_f]
            print(phys_mem[next_f])
            # Retrieve from physical memory
            # Print all the stuff

    fault_rate = faults / misses
    hit_rate = hits / misses

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
    num_frames = int(argv[3])

    addresses = get_addresses(ref_seq_filename)

    backing_store = open('BACKING_STORE.bin', 'rb')
    
    if algo == 'FIFO':
        page_faults, page_fault_rate, tlb_hits, tlb_misses, tlb_hit_rate = fifo(addresses, num_frames, backing_store)
    elif algo == 'LRU':
        page_faults, page_fault_rate, tlb_hits, tlb_misses, tlb_hit_rate = lru(addresses)
    elif algo == 'OPT':
        page_faults, page_fault_rate, tlb_hits, tlb_misses, tlb_hit_rate = opt(addresses)
    else:
        raise(ValueError(f'Invalid algorithm: {algo}'))
    
    print(f'Number of Translated Addresses = {len(addresses)}')
    print(f'Page Faults = {page_faults}')
    print('Page Fault Rate = %.3f' % page_fault_rate)
    print(f'TLB Hits = {tlb_hits}')
    print(f'TLB Misses = {tlb_misses}')
    print('TLB Hit Rate = %.3f' % tlb_hit_rate)

if __name__ == '__main__':
    main(sys.argv)
