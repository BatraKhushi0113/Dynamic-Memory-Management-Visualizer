def run(pages, capacity):
    memory = []
    recent = []
    faults = 0
    history = []
    events = []

    for page in pages:
        if page not in memory:
            faults += 1
            if len(memory) < capacity:
                memory.append(page)
                recent.append(page)
                events.append(f"Page Fault: {page} loaded into free frame.")
            else:
                lru_page = recent.pop(0)
                idx = memory.index(lru_page)
                memory[idx] = page
                recent.append(page)
                events.append(f"Page Fault: {lru_page} replaced by {page} using LRU.")
        else:
            recent.remove(page)
            recent.append(page)
            events.append(f"Page Hit: {page} already in memory.")

        if page in recent:
            if recent.count(page) > 1:
                recent = [x for i, x in enumerate(recent) if x != page or i == len(recent)-1]

        if page in memory and page not in recent:
            recent.append(page)

        history.append(memory.copy())

    hits = len(pages) - faults
    hit_ratio = (hits / len(pages)) * 100 if pages else 0

    return {
        "name": "LRU",
        "pages": pages,
        "capacity": capacity,
        "faults": faults,
        "hits": hits,
        "hit_ratio": hit_ratio,
        "history": history,
        "events": events
    }