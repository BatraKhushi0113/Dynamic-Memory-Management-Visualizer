"""
visualizer.py - Visualization data preparation
Converts simulation results into chart-ready data structures
"""

import json
from typing import Optional
from algorithms import FIFO, LRU, compare_algorithms, ReplacementStep
from memory import Memory, Process, VirtualMemory


def build_timeline_data(steps: list[dict], reference_string: list[int], num_frames: int) -> dict:
    """
    Build timeline matrix for heatmap-style visualization.
    Returns frame states at each step.
    """
    matrix = []  # rows = frames, cols = steps
    fault_markers = []

    for step in steps:
        snapshot = step["frames_snapshot"]
        frame_pages = [snap[1] for snap in snapshot]  # None or page_id
        matrix.append(frame_pages)
        fault_markers.append(1 if step["is_fault"] else 0)

    # Transpose: rows=frames, cols=steps
    transposed = []
    for frame_idx in range(num_frames):
        row = []
        for step_frame_pages in matrix:
            row.append(step_frame_pages[frame_idx] if frame_idx < len(step_frame_pages) else None)
        transposed.append(row)

    return {
        "matrix": transposed,
        "fault_markers": fault_markers,
        "steps": list(range(len(steps))),
        "frames": list(range(num_frames)),
        "reference_string": reference_string,
    }


def build_fault_curve(steps: list[dict]) -> dict:
    """Build cumulative fault curve data"""
    x = []
    y_faults = []
    y_hits = []

    for step in steps:
        x.append(step["step"])
        y_faults.append(step["fault_count"])
        y_hits.append(step["hit_count"])

    return {"x": x, "faults": y_faults, "hits": y_hits}


def build_comparison_bar(fifo_metrics: dict, lru_metrics: dict) -> dict:
    """Build bar chart data comparing FIFO vs LRU"""
    return {
        "algorithms": ["FIFO", "LRU"],
        "page_faults": [fifo_metrics["page_faults"], lru_metrics["page_faults"]],
        "page_hits": [fifo_metrics["page_hits"], lru_metrics["page_hits"]],
        "fault_rates": [
            round(fifo_metrics["fault_rate"] * 100, 1),
            round(lru_metrics["fault_rate"] * 100, 1),
        ],
        "hit_rates": [
            round(fifo_metrics["hit_rate"] * 100, 1),
            round(lru_metrics["hit_rate"] * 100, 1),
        ],
    }


def build_memory_map(memory: Memory) -> dict:
    """Build memory block visualization data"""
    blocks = []
    for frame in memory.frames:
        blocks.append({
            "frame_id": frame.frame_id,
            "page_id": frame.page_id,
            "process_id": frame.process_id,
            "is_free": frame.is_free,
            "label": f"P{frame.process_id}/Pg{frame.page_id}" if not frame.is_free else "FREE",
        })
    return {"blocks": blocks, "num_frames": memory.num_frames}


def build_segmentation_data(process: Process) -> dict:
    """Build segmentation visualization data"""
    segments = []
    total = sum(s.limit for s in process.segments)
    for seg in process.segments:
        segments.append({
            "name": seg.name,
            "base": seg.base,
            "limit": seg.limit,
            "end": seg.base + seg.limit,
            "pct": seg.limit / total * 100 if total else 0,
        })
    return {"segments": segments, "process_id": process.process_id}


def build_virtual_memory_diagram(process: Process, memory: Memory, page_size: int) -> dict:
    """Show logical → physical address mapping"""
    mappings = []
    for page_id, entry in process.page_table.entries.items():
        logical_start = page_id * page_size
        physical_start = entry.frame_id * page_size if entry.frame_id is not None else None
        mappings.append({
            "page_id": page_id,
            "logical_start": logical_start,
            "logical_end": logical_start + page_size,
            "frame_id": entry.frame_id,
            "physical_start": physical_start,
            "physical_end": physical_start + page_size if physical_start is not None else None,
            "valid": entry.valid,
            "in_disk": not entry.valid,
        })
    return {"mappings": mappings, "page_size": page_size}


def generate_full_report(
    reference_string: list[int],
    num_frames: int,
    total_memory: int,
    page_size: int,
    num_processes: int,
) -> dict:
    """
    Master function: run simulation and return all chart data as JSON-serializable dict.
    """
    # Run algorithms
    comparison = compare_algorithms(reference_string, num_frames)

    fifo_steps = comparison["fifo_steps"]
    lru_steps = comparison["lru_steps"]
    fifo_metrics = comparison["fifo"]
    lru_metrics = comparison["lru"]

    # Build memory object
    memory = Memory(total_memory, page_size)

    # Build processes
    pages_per_proc = max(1, len(set(reference_string)) // num_processes)
    processes = [
        Process(i, f"Process-{i}", pages_per_proc, page_size)
        for i in range(num_processes)
    ]

    return {
        "fifo": {
            "steps": fifo_steps,
            "metrics": fifo_metrics,
            "timeline": build_timeline_data(fifo_steps, reference_string, num_frames),
            "fault_curve": build_fault_curve(fifo_steps),
        },
        "lru": {
            "steps": lru_steps,
            "metrics": lru_metrics,
            "timeline": build_timeline_data(lru_steps, reference_string, num_frames),
            "fault_curve": build_fault_curve(lru_steps),
        },
        "comparison": build_comparison_bar(fifo_metrics, lru_metrics),
        "memory_map": build_memory_map(memory),
        "segmentation": [build_segmentation_data(p) for p in processes],
        "virtual_memory": build_virtual_memory_diagram(processes[0], memory, page_size) if processes else {},
        "config": {
            "reference_string": reference_string,
            "num_frames": num_frames,
            "total_memory": total_memory,
            "page_size": page_size,
            "num_processes": num_processes,
        },
    }
