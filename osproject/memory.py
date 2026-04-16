"""
memory.py - Core memory management logic
Handles paging, segmentation, and virtual memory simulation
"""

from dataclasses import dataclass, field
from typing import Optional
import math


@dataclass
class Frame:
    """Represents a physical memory frame"""
    frame_id: int
    page_id: Optional[int] = None
    process_id: Optional[int] = None
    loaded_at: int = 0  # timestamp when page was loaded
    last_used: int = 0  # timestamp when last accessed (for LRU)
    is_free: bool = True

    def load_page(self, page_id: int, process_id: int, timestamp: int):
        self.page_id = page_id
        self.process_id = process_id
        self.loaded_at = timestamp
        self.last_used = timestamp
        self.is_free = False

    def free(self):
        self.page_id = None
        self.process_id = None
        self.loaded_at = 0
        self.last_used = 0
        self.is_free = True

    def to_dict(self):
        return {
            "frame_id": self.frame_id,
            "page_id": self.page_id,
            "process_id": self.process_id,
            "loaded_at": self.loaded_at,
            "last_used": self.last_used,
            "is_free": self.is_free,
        }


@dataclass
class PageTableEntry:
    """Single entry in a page table"""
    page_id: int
    frame_id: Optional[int] = None
    valid: bool = False  # True if page is in physical memory
    dirty: bool = False  # True if page has been modified
    referenced: bool = False

    def to_dict(self):
        return {
            "page_id": self.page_id,
            "frame_id": self.frame_id,
            "valid": self.valid,
            "dirty": self.dirty,
            "referenced": self.referenced,
        }


class PageTable:
    """
    Page table for a single process.
    Maps logical page numbers to physical frame numbers.
    """

    def __init__(self, process_id: int, num_pages: int):
        self.process_id = process_id
        self.num_pages = num_pages
        self.entries: dict[int, PageTableEntry] = {
            i: PageTableEntry(page_id=i) for i in range(num_pages)
        }

    def map_page(self, page_id: int, frame_id: int):
        if page_id in self.entries:
            self.entries[page_id].frame_id = frame_id
            self.entries[page_id].valid = True

    def unmap_page(self, page_id: int):
        if page_id in self.entries:
            self.entries[page_id].frame_id = None
            self.entries[page_id].valid = False

    def get_frame(self, page_id: int) -> Optional[int]:
        entry = self.entries.get(page_id)
        if entry and entry.valid:
            return entry.frame_id
        return None

    def to_dict(self):
        return {pid: e.to_dict() for pid, e in self.entries.items()}


@dataclass
class Segment:
    """Represents a memory segment (for segmentation)"""
    segment_id: int
    name: str
    base: int
    limit: int
    process_id: int

    def to_dict(self):
        return {
            "segment_id": self.segment_id,
            "name": self.name,
            "base": self.base,
            "limit": self.limit,
            "process_id": self.process_id,
        }


class Process:
    """
    Represents an OS process with its memory requirements.
    """

    def __init__(self, process_id: int, name: str, num_pages: int, page_size: int):
        self.process_id = process_id
        self.name = name
        self.num_pages = num_pages
        self.page_size = page_size
        self.page_table = PageTable(process_id, num_pages)
        self.segments: list[Segment] = []
        self._init_segments()

    def _init_segments(self):
        """Create typical OS process segments: Code, Stack, Heap, Data"""
        seg_names = ["Code", "Data", "Stack", "Heap"]
        base = 0
        for i, name in enumerate(seg_names[:self.num_pages]):
            limit = self.page_size * max(1, self.num_pages // 4)
            self.segments.append(Segment(
                segment_id=i,
                name=name,
                base=base,
                limit=limit,
                process_id=self.process_id,
            ))
            base += limit

    def to_dict(self):
        return {
            "process_id": self.process_id,
            "name": self.name,
            "num_pages": self.num_pages,
            "page_size": self.page_size,
            "page_table": self.page_table.to_dict(),
            "segments": [s.to_dict() for s in self.segments],
        }


class Memory:
    """
    Simulates physical memory as a collection of frames.
    """

    def __init__(self, total_size: int, frame_size: int):
        self.total_size = total_size
        self.frame_size = frame_size
        self.num_frames = total_size // frame_size
        self.frames: list[Frame] = [Frame(frame_id=i) for i in range(self.num_frames)]

    def get_free_frame(self) -> Optional[Frame]:
        for frame in self.frames:
            if frame.is_free:
                return frame
        return None

    def has_free_frame(self) -> bool:
        return any(f.is_free for f in self.frames)

    def get_occupied_frames(self) -> list[Frame]:
        return [f for f in self.frames if not f.is_free]

    def utilization(self) -> float:
        occupied = sum(1 for f in self.frames if not f.is_free)
        return occupied / self.num_frames if self.num_frames > 0 else 0

    def to_dict(self):
        return {
            "total_size": self.total_size,
            "frame_size": self.frame_size,
            "num_frames": self.num_frames,
            "frames": [f.to_dict() for f in self.frames],
            "utilization": self.utilization(),
        }


class VirtualMemory:
    """
    Simulates virtual memory mapping between logical and physical addresses.
    """

    def __init__(self, memory: Memory, page_size: int):
        self.memory = memory
        self.page_size = page_size
        self.disk_pages: dict[tuple, bool] = {}  # (process_id, page_id) -> on disk

    def translate_address(self, process: Process, logical_address: int) -> dict:
        """Translate logical address to physical address"""
        page_id = logical_address // self.page_size
        offset = logical_address % self.page_size

        frame_id = process.page_table.get_frame(page_id)
        if frame_id is None:
            return {
                "success": False,
                "page_id": page_id,
                "offset": offset,
                "physical_address": None,
                "page_fault": True,
            }

        physical_address = frame_id * self.page_size + offset
        return {
            "success": True,
            "page_id": page_id,
            "offset": offset,
            "frame_id": frame_id,
            "physical_address": physical_address,
            "page_fault": False,
        }
