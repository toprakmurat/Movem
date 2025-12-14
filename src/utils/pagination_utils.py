import math
from dataclasses import dataclass
from typing import List, Any

@dataclass
class Pagination:
    items: List[Any]
    page: int = 1
    per_page: int = 8
    total_count: int = 0

    @property
    def total(self) -> int:
        return self.total_count
    
    @property
    def pages(self) -> int: 
        if self.total_count == 0 or self.per_page == 0:
            return 1
        return int(math.ceil(self.total_count / self.per_page))

    def start_index(self) -> int:
        if not self.items:
            return 0
        return (self.page - 1) * self.per_page + 1

    def end_index(self) -> int:
        return min(self.page * self.per_page, self.total_count)

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.pages 

    @property
    def prev_num(self) -> int:
        return max(1, self.page - 1)

    @property
    def next_num(self) -> int:
        return self.page + 1