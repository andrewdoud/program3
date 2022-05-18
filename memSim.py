from io import BufferedReader
import sys

PAGE_SIZE = 256
TLB_SIZE = 16

# offset + page_num -> read 256 bytes

def search_tlb(tlb, p):
    for i in range(len(tlb)):
        entry = tlb[i] # (p, f)
        if entry[0] == p:
            return i 
    return -1

def fifo(addresses, num_frames: int, backing_store: BufferedReader):
    faults = fault_rate = hits = misses = hit_rate = 0 # Metrics

    # init tlb
    tlb = [(None, None)] * TLB_SIZE
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
        tlb_i = search_tlb(tlb, p) # (p, f)
        if tlb_i == -1 or tlb[tlb_i][1] is None: # if miss
            misses += 1
            # print('miss')

            # Check if valid in the page table
            if page_table[p][1] == 1: # if already in physical mem
                f = page_table[p][0]
                # Retrieve from physical memory
                phys_entry = phys_mem[f]
                ref_byte_int = phys_entry[0]
                hex_data = phys_entry[1]
                print(f'{addr}, {ref_byte_int}, {f}, {hex_data}')
                # Print all the stuff

            else: # if not in physical mem yet, replace curr frame in physical mem
                faults += 1
                # print('fault')
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
                    page_table[old_p] = (f, None) # Clear the old page table entry
                    old_p_tlb = search_tlb(tlb, old_p)
                    if old_p_tlb != -1:
                        tlb[old_p_tlb] = (f, None) # Clear the old tlb entry (if exists)

                frame_p[f] = p
                phys_mem[f] = (ref_byte_int, hex_data)

                # Increment the frame number (since FIFO goes to 0 if past end)
                next_f += 1
                if next_f >= num_frames:
                    next_f = 0

            # If p already in tlb, update tlb entry
            if tlb_i != -1:
                tlb[tlb_i] = (p, f)
            # Else, replace tlb entry (fifo)
            else:
                tlb[tlb_p] = (p, f)
                # Increment tlb pointer (goes to 0 if past end)
                tlb_p += 1
                if tlb_p >= TLB_SIZE:
                    tlb_p = 0

        else: # if hit
            hits += 1
            # print('hit')
            # Find in page table
            entry = tlb[tlb_i]
            f = entry[1]
            # Retrieve from physical memory
            phys_entry = phys_mem[f]
            ref_byte_int = phys_entry[0]
            hex_data = phys_entry[1]
            # Print all the stuff
            print(f'{addr}, {ref_byte_int}, {f}, {hex_data}')

    fault_rate = faults / (misses + hits)
    hit_rate = hits / (misses + hits)

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
