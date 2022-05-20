import sys

PAGE_SIZE = 256
TLB_SIZE = 16

def search_tlb(tlb, p):
    for i in range(len(tlb)):
        entry = tlb[i] # (p, f)
        if entry[0] == p:
            return i
    return -1

def fifo(next_f, num_frames):
    next_f += 1
    if next_f >= num_frames:
        next_f = 0
    return next_f

def lru(lru_q):
    return lru_q[0]

def opt(next_addresses, frame_p):
    next_ps = [addr // PAGE_SIZE for addr in next_addresses]
    latest_f = None
    time_to_latest_p = 0
    for f in range(len(frame_p)):
        p = frame_p[f]
        # if the beginning sequence, just return the next f
        if p is None:
            return f
        # if p will never get used again, break
        if p not in next_ps:
            return f
        i = 1
        for next_p in next_ps:
            if next_p == p:
                if i > time_to_latest_p: # Potential grading disputes here
                    latest_f = f
                    time_to_latest_p = i
    return latest_f

def mem_sim(addresses, num_frames, backing_store, algorithm):
    ## Initialize everything
    
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

    # init lru queue (used across algos b/c doesn't affect anything unless lru)
    lru_q = list(range(num_frames))

    ## Start reading addresses

    for i in range(len(addresses)):
        addr = addresses[i]
        # Get page num, offset and backing storage address
        p = addr // PAGE_SIZE # page number
        d = addr % PAGE_SIZE # page offset
        back_addr = p * PAGE_SIZE # backing storage address

        # Update next_f if not using FIFO
        if algorithm == 'LRU':
            next_f = lru(lru_q)
        elif algorithm == 'OPT':
            next_f = opt(addresses[i+1:], frame_p)
        
        print(frame_p)
        print(tlb)

        # Try to grab entry from tlb
        tlb_i = search_tlb(tlb, p) # (p, f)
        if tlb_i == -1 or tlb[tlb_i][1] is None: # if miss
            misses += 1
            print('miss')

            # Check if valid in the page table
            if page_table[p][1] == 1: # if already in physical mem
                # Get f from page table (soft miss)
                f = page_table[p][0]

                # Move lru queue since frame is touched
                f_i = lru_q.index(f)
                lru_q.pop(f_i)
                lru_q.append(f)

                # Retrieve from physical memory
                phys_entry = phys_mem[f]
                ref_byte_int = phys_entry[0]
                hex_data = phys_entry[1]

                # Print all the stuff
                print(f'{addr}, {ref_byte_int}, {p}, {f}, {hex_data}')

            else: # if not in physical mem yet, replace curr frame in physical mem
                faults += 1
                print('fault')
                f = next_f

                # Retrieve data from backing store
                backing_store.seek(back_addr, 0)
                hex_data = backing_store.read(PAGE_SIZE).hex().upper()

                # Retrieve reference bit from backing store
                backing_store.seek(back_addr + d, 0)
                ref_byte = backing_store.read(1)
                ref_byte_int = int.from_bytes(ref_byte, 'little', signed=True)

                # Print all the stuff
                print(f'{addr}, {ref_byte_int}, {p}, {f}, {hex_data}')

                # Update page table
                page_table[p] = (f, 1)

                # Update physical memory
                if frame_p[f] is not None: # If phys mem already has entry in curr frame
                    old_p = frame_p[f]
                    page_table[old_p] = (f, None) # Clear the old page table entry
                    old_p_tlb = search_tlb(tlb, old_p)
                    if old_p_tlb != -1:
                        tlb.pop(old_p_tlb) # Clear the old tlb entry (if exists)
                        tlb.append((None, None))
                        if old_p_tlb < tlb_p:
                            tlb_p -= 1

                # Make f point to new p
                frame_p[f] = p
                # Replace frame with new byte and data
                phys_mem[f] = (ref_byte_int, hex_data)
                
                f_i = lru_q.index(f)
                lru_q.pop(f_i)
                lru_q.append(f)

                # Get the next frame if fifo (only changes next frame after a frame gets altered rather than any time a frame is touched)
                if algorithm == 'FIFO':
                    next_f = fifo(next_f, num_frames)

            # If p already in tlb, update tlb entry
            if tlb_i != -1:
                tlb.pop(tlb_i)
                if tlb_i < tlb_p:
                    tlb_p -= 1
            # Add the new entry
            tlb[tlb_p] = (p, f)
            # Increment tlb pointer (goes to 0 if past end)
            tlb_p += 1
            if tlb_p >= TLB_SIZE:
                tlb_p = 0

        else: # if hit
            hits += 1
            print('hit')

            # Find in page table
            entry = tlb[tlb_i]
            f = entry[1]

            # Move lru queue since frame is touched
            f_i = lru_q.index(f)
            lru_q.pop(f_i)
            lru_q.append(f)

            # Retrieve from physical memory
            phys_entry = phys_mem[f]
            ref_byte_int = phys_entry[0]
            hex_data = phys_entry[1]
            # Print all the stuff
            print(f'{addr}, {ref_byte_int}, {p}, {f}, {hex_data}')

    # Calc metrics
    fault_rate = faults / (misses + hits)
    hit_rate = hits / (misses + hits)

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
    num_frames = int(argv[2])
    algorithm = argv[3]

    addresses = get_addresses(ref_seq_filename)

    backing_store = open('BACKING_STORE.bin', 'rb')
    
    page_faults, page_fault_rate, tlb_hits, tlb_misses, tlb_hit_rate = \
        mem_sim(addresses, num_frames, backing_store, algorithm)
    
    print(f'Number of Translated Addresses = {len(addresses)}')
    print(f'Page Faults = {page_faults}')
    print('Page Fault Rate = %.3f' % page_fault_rate)
    print(f'TLB Hits = {tlb_hits}')
    print(f'TLB Misses = {tlb_misses}')
    print('TLB Hit Rate = %.3f' % tlb_hit_rate)

if __name__ == '__main__':
    main(sys.argv)
