def run(pages, capacity):
    memory = []
    queue = []
    faults = 0
    history = []
    events = []

    for page in pages:
        if page not in memory:
            faults += 1
            if len(memory) < capacity:
                memory.append(page)
                queue.append(page)
                events.append(f"Page Fault: {page} loaded into free frame.")
            else:
                removed = queue.pop(0)
                idx = memory.index(removed)
                memory[idx] = page
                queue.append(page)
                events.append(f"Page Fault: {removed} replaced by {page} using FIFO.")
        else:
            events.append(f"Page Hit: {page} already in memory.")

        history.append(memory.copy())

    hits = len(pages) - faults
    hit_ratio = (hits / len(pages)) * 100 if pages else 0

    return {
        "name": "FIFO",
        "pages": pages,
        "capacity": capacity,
        "faults": faults,
        "hits": hits,
        "hit_ratio": hit_ratio,
        "history": history,
        "events": events
    }