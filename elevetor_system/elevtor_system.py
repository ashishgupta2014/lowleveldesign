from typing import List, Optional

from elevetor_system.lift import Lift


class ElevatorSystem:
    def __init__(self):
        self.lifts: List[Lift] = []
        self.total_floors = 0

    def init(self, floors: int, lifts: int):
        self.total_floors = floors
        self.lifts = [Lift(lift_id=i) for i in range(lifts)]

    def request_lift(self, start_floor: int, destination_floor: int) -> int:
        best_lift: Optional[Lift] = None
        best_time = float("inf")

        for lift in self.lifts:
            if not lift.is_eligible(start_floor, destination_floor):
                continue
            time = lift.estimated_time_to_reach(start_floor)
            if time < best_time:
                best_time = time
                best_lift = lift

        if best_lift:
            best_lift.add_request(start_floor, destination_floor)
            return best_lift.lift_id
        return -1

    def tick(self):
        for lift in self.lifts:
            lift.tick()

    def get_lift_states(self) -> List[str]:
        return [lift.get_state() for lift in self.lifts]

    def get_lifts_stopping_on_floor(self, floor: int, move_direction: str) -> List[int]:
        return [
            lift.lift_id
            for lift in self.lifts
            if lift.will_stop_at(floor, move_direction)
        ]