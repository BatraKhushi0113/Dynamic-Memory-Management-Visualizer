"""
algorithms.py - Page Replacement Algorithm Implementations
Provides FIFO and LRU page replacement with full step logging
"""

from collections import deque
from dataclasses import dataclass, field
from typing import Optional
from memory import Memory, Process, Frame


@dataclass
class ReplacementStep:
    """Records a single step in the page replacement simulation"""
    step: int
    page_requested: int
    is_fault: bool
    evicted_page: Optional[int]
    evicted_frame: Optional[int]
    loaded_frame: int
    frames_snapshot: list  # list of (frame_id, page_id) tuples
    fault_count_so_far: int
    hit_count_so_far: int
    algorithm: str

    def to_dict(self):
        return {
            "step": self.step,
            "page_requested": self.page_requested,
            "is_fault": self.is_fault,
            "evicted_page": self.evicted_page,
            "evicted_frame": self.evicted_frame,
            "loaded_frame": self.loaded_frame,
            "frames_snapshot": self.frames_snapshot,
            "fault_count": self.fault_count_so_far,
            "hit_count": self.hit_count_so_far,
            "algorithm": self.algorithm,
        }


class ReplacementAlgorithm:
    """Base class for page replacement algorithms"""

    def __init__(self, num_frames: int):
        self.num_frames = num_frames
        self.steps: list[ReplacementStep] = []
        self.fault_count = 0
        self.hit_count = 0
        self.frames: list[Optional[int]] = [None] * num_frames  # stores page_ids

    def reset(self):
        self.steps = []
        self.fault_count = 0
        self.hit_count = 0
        self.frames = [None] * self.num_frames

    def is_page_in_memory(self, page: int) -> bool:
        return page in self.frames

    def get_free_slot(self) -> int:
        """Return index of first free frame slot, or -1 if none"""
        for i, p in enumerate(self.frames):
            if p is None:
                return i
        return -1

    def snapshot(self) -> list:
        return [(i, p) for i, p in enumerate(self.frames)]

    def run(self, reference_string: list[int]) -> list[ReplacementStep]:
        raise NotImplementedError


class FIFO(ReplacementAlgorithm):
    """
    First-In First-Out page replacement.
    Replaces the page that has been in memory the longest.
    """

    def __init__(self, num_frames: int):
        super().__init__(num_frames)
        self.queue: deque = deque()  # tracks arrival order

    def reset(self):
        super().reset()
        self.queue = deque()

    def run(self, reference_string: list[int]) -> list[ReplacementStep]:
        self.reset()

        for step_num, page in enumerate(reference_string):
            if self.is_page_in_memory(page):
                # Page HIT
                self.hit_count += 1
                self.steps.append(ReplacementStep(
                    step=step_num,
                    page_requested=page,
                    is_fault=False,
                    evicted_page=None,
                    evicted_frame=None,
                    loaded_frame=self.frames.index(page),
                    frames_snapshot=self.snapshot(),
                    fault_count_so_far=self.fault_count,
                    hit_count_so_far=self.hit_count,
                    algorithm="FIFO",
                ))
            else:
                # Page FAULT
                self.fault_count += 1
                free_slot = self.get_free_slot()

                if free_slot != -1:
                    # Load into free slot
                    self.frames[free_slot] = page
                    self.queue.append(free_slot)
                    self.steps.append(ReplacementStep(
                        step=step_num,
                        page_requested=page,
                        is_fault=True,
                        evicted_page=None,
                        evicted_frame=None,
                        loaded_frame=free_slot,
                        frames_snapshot=self.snapshot(),
                        fault_count_so_far=self.fault_count,
                        hit_count_so_far=self.hit_count,
                        algorithm="FIFO",
                    ))
                else:
                    # Evict oldest page (front of queue)
                    victim_slot = self.queue.popleft()
                    evicted_page = self.frames[victim_slot]
                    self.frames[victim_slot] = page
                    self.queue.append(victim_slot)
                    self.steps.append(ReplacementStep(
                        step=step_num,
                        page_requested=page,
                        is_fault=True,
                        evicted_page=evicted_page,
                        evicted_frame=victim_slot,
                        loaded_frame=victim_slot,
                        frames_snapshot=self.snapshot(),
                        fault_count_so_far=self.fault_count,
                        hit_count_so_far=self.hit_count,
                        algorithm="FIFO",
                    ))

        return self.steps

    def get_metrics(self, total_references: int) -> dict:
        return {
            "algorithm": "FIFO",
            "total_references": total_references,
            "page_faults": self.fault_count,
            "page_hits": self.hit_count,
            "fault_rate": self.fault_count / total_references if total_references else 0,
            "hit_rate": self.hit_count / total_references if total_references else 0,
        }


class LRU(ReplacementAlgorithm):
    """
    Least Recently Used page replacement.
    Replaces the page that hasn't been used for the longest time.
    """

    def __init__(self, num_frames: int):
        super().__init__(num_frames)
        self.usage_order: list[int] = []  # tracks usage recency (index = frame slot)

    def reset(self):
        super().reset()
        self.usage_order = []

    def _update_usage(self, slot: int):
        """Move slot to end of usage list (most recently used)"""
        if slot in self.usage_order:
            self.usage_order.remove(slot)
        self.usage_order.append(slot)

    def _get_lru_slot(self) -> int:
        """Return the least recently used frame slot"""
        return self.usage_order[0]

    def run(self, reference_string: list[int]) -> list[ReplacementStep]:
        self.reset()

        for step_num, page in enumerate(reference_string):
            if self.is_page_in_memory(page):
                # Page HIT - update recency
                self.hit_count += 1
                slot = self.frames.index(page)
                self._update_usage(slot)
                self.steps.append(ReplacementStep(
                    step=step_num,
                    page_requested=page,
                    is_fault=False,
                    evicted_page=None,
                    evicted_frame=None,
                    loaded_frame=slot,
                    frames_snapshot=self.snapshot(),
                    fault_count_so_far=self.fault_count,
                    hit_count_so_far=self.hit_count,
                    algorithm="LRU",
                ))
            else:
                # Page FAULT
                self.fault_count += 1
                free_slot = self.get_free_slot()

                if free_slot != -1:
                    # Load into free slot
                    self.frames[free_slot] = page
                    self._update_usage(free_slot)
                    self.steps.append(ReplacementStep(
                        step=step_num,
                        page_requested=page,
                        is_fault=True,
                        evicted_page=None,
                        evicted_frame=None,
                        loaded_frame=free_slot,
                        frames_snapshot=self.snapshot(),
                        fault_count_so_far=self.fault_count,
                        hit_count_so_far=self.hit_count,
                        algorithm="LRU",
                    ))
                else:
                    # Evict LRU page
                    victim_slot = self._get_lru_slot()
                    evicted_page = self.frames[victim_slot]
                    self.frames[victim_slot] = page
                    self._update_usage(victim_slot)
                    self.steps.append(ReplacementStep(
                        step=step_num,
                        page_requested=page,
                        is_fault=True,
                        evicted_page=evicted_page,
                        evicted_frame=victim_slot,
                        loaded_frame=victim_slot,
                        frames_snapshot=self.snapshot(),
                        fault_count_so_far=self.fault_count,
                        hit_count_so_far=self.hit_count,
                        algorithm="LRU",
                    ))

        return self.steps

    def get_metrics(self, total_references: int) -> dict:
        return {
            "algorithm": "LRU",
            "total_references": total_references,
            "page_faults": self.fault_count,
            "page_hits": self.hit_count,
            "fault_rate": self.fault_count / total_references if total_references else 0,
            "hit_rate": self.hit_count / total_references if total_references else 0,
        }


def compare_algorithms(reference_string: list[int], num_frames: int) -> dict:
    """Run both algorithms on same input and return comparison data"""
    fifo = FIFO(num_frames)
    lru = LRU(num_frames)

    fifo_steps = fifo.run(reference_string)
    lru_steps = lru.run(reference_string)

    n = len(reference_string)
    return {
        "fifo": fifo.get_metrics(n),
        "lru": lru.get_metrics(n),
        "fifo_steps": [s.to_dict() for s in fifo_steps],
        "lru_steps": [s.to_dict() for s in lru_steps],
        "reference_string": reference_string,
        "num_frames": num_frames,
    }
