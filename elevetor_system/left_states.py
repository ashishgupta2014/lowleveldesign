from abc import ABC, abstractmethod
from enum import Enum


class Direction(Enum):
    IDLE = "I"
    UP = "U"
    DOWN = "D"


class LiftState(ABC):
    @abstractmethod
    def move(self, lift: "Lift"):
        pass

    @abstractmethod
    def get_direction(self) -> Direction:
        pass


class IdleState(LiftState):
    def move(self, lift: "Lift"):
        # Check if there's something to do
        if lift.passengers:
            dest = lift.passengers[0][1]
        elif lift.pickup_queue:
            dest = lift.pickup_queue[0].start
            if lift.current_floor == dest:
                dest = lift.pickup_queue[0].dest
        else:
            return  # Remain idle

        if dest > lift.current_floor:
            lift.change_state(MovingUpState())
        elif dest < lift.current_floor:
            lift.change_state(MovingDownState())

    def get_direction(self) -> Direction:
        return Direction.IDLE


class MovingUpState(LiftState):
    def move(self, lift: "Lift"):
        lift.current_floor += 1
        lift.unload_passengers()
        lift.load_passengers()

        if not lift.has_more_stops(Direction.UP):
            if lift.has_more_stops(Direction.DOWN):
                lift.change_state(MovingDownState())
            else:
                lift.change_state(IdleState())

    def get_direction(self) -> Direction:
        return Direction.UP


class MovingDownState(LiftState):
    def move(self, lift: "Lift"):
        lift.current_floor -= 1
        lift.unload_passengers()
        lift.load_passengers()

        if not lift.has_more_stops(Direction.DOWN):
            if lift.has_more_stops(Direction.UP):
                lift.change_state(MovingUpState())
            else:
                lift.change_state(IdleState())

    def get_direction(self) -> Direction:
        return Direction.DOWN
