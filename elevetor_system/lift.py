from typing import List, Tuple

from elevetor_system.left_states import LiftState, IdleState, Direction


class Request:
    def __init__(self, start: int, dest: int):
        self.start = start
        self.dest = dest
        self.direction = Direction.UP if dest > start else Direction.DOWN


class Lift:
    def __init__(self, lift_id: int):
        self.lift_id = lift_id
        self.current_floor = 0
        self.capacity = 10
        self.passengers: List[Tuple[int, int]] = []
        self.pickup_queue: List[Request] = []
        self.stop_floors: set = set()
        self.state: LiftState = IdleState()

    def change_state(self, new_state: LiftState):
        self.state = new_state

    def is_eligible(self, start: int, dest: int) -> bool:
        req_dir = Direction.UP if dest > start else Direction.DOWN
        curr_dir = self.state.get_direction()
        if curr_dir == Direction.IDLE:
            return True
        if curr_dir != req_dir:
            return False
        if curr_dir == Direction.UP and self.current_floor > start:
            return False
        if curr_dir == Direction.DOWN and self.current_floor < start:
            return False
        return True

    def estimated_time_to_reach(self, start: int) -> int:
        return abs(self.current_floor - start)

    def add_request(self, start: int, dest: int):
        self.pickup_queue.append(Request(start, dest))
        self.stop_floors.add(start)
        self.stop_floors.add(dest)
        # if self.state.get_direction().value == 'I':
        #     self.tick()

    def tick(self):
        self.state.move(self)

    def unload_passengers(self):
        self.passengers = [p for p in self.passengers if p[1] != self.current_floor]
        self.stop_floors.discard(self.current_floor)

    def load_passengers(self):
        to_pick = [req for req in self.pickup_queue if req.start == self.current_floor]
        for req in to_pick:
            if len(self.passengers) < self.capacity:
                self.passengers.append((req.start, req.dest))
                self.pickup_queue.remove(req)
        self.stop_floors.discard(self.current_floor)

    def has_more_stops(self, direction: Direction) -> bool:
        if direction == Direction.UP:
            return any(f > self.current_floor for f in self.stop_floors)
        if direction == Direction.DOWN:
            return any(f < self.current_floor for f in self.stop_floors)
        return False

    def will_stop_at(self, floor: int, move_dir: str) -> bool:
        return floor in self.stop_floors and self.state.get_direction().value == move_dir

    def get_state(self) -> str:
        return f"{self.current_floor}-{self.state.get_direction().value}"
