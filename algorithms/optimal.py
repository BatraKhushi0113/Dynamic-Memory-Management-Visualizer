def run(pages, capacity):
    memory = []
    faults = 0
    history = []
    events = []

    for i, page in enumerate(pages):

        # Page HIT
        if page in memory:
            events.append(f"Page Hit: {page} already in memory.")
            history.append(memory.copy())
            continue

        # Page FAULT
        faults += 1

        # If memory has space
        if len(memory) < capacity:
            memory.append(page)
            events.append(f"Page Fault: {page} loaded into free frame.")
        else:
            # Find page to replace (farthest future use)
            future_use = {}

            for m in memory:
                if m in pages[i+1:]:
                    future_use[m] = pages[i+1:].index(m)
                else:
                    future_use[m] = float('inf')

            # Replace page with max future distance
            page_to_replace = max(future_use, key=future_use.get)
            idx = memory.index(page_to_replace)
            memory[idx] = page

            events.append(f"Page Fault: {page_to_replace} replaced by {page} using OPTIMAL.")

        history.append(memory.copy())

    hits = len(pages) - faults
    hit_ratio = (hits / len(pages)) * 100 if pages else 0

    return {
        "name": "OPTIMAL",
        "pages": pages,
        "capacity": capacity,
        "faults": faults,
        "hits": hits,
        "hit_ratio": hit_ratio,
        "history": history,
        "events": events
    }