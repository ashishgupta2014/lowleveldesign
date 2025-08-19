import datetime
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict


# ------------------ Core Models ------------------

class ParkingSpot:
    def __init__(self, floor, row, column, vehicle_type, can_park=True, vehicle_number=None):
        self.floor = floor
        self.row = row
        self.column = column
        self.vehicle_type = int(vehicle_type)  # 2 or 4
        self.vehicle_number = vehicle_number
        self.can_park = can_park  # True means currently free/allowed to park

    def is_parking_available(self):
        return self.can_park and self.vehicle_number is None

    def remove_parking(self):
        self.can_park = True
        self.vehicle_number = None

    def get_spot_id(self):
        return f"{self.floor}-{self.row}-{self.column}"

    def park(self, vehicle_type, vehicle_number):
        if self.is_parking_available() and self.vehicle_type == vehicle_type:
            self.can_park = False
            self.vehicle_number = vehicle_number
            return True
        return False

    def display(self):
        print("--------------SPOT DISPLAY-------------------")
        print(f"spotId:                  {self.get_spot_id()}")
        print(f"FloorNumber:             {self.floor}")
        print(f"RowNumber:               {self.row}")
        print(f"ColumnNumber:            {self.column}")
        print(f"VehicleType:             {self.vehicle_type}")
        print(f"canParkVehicle:          {self.can_park}")
        print(f"parkedVehicleNumber:     {self.vehicle_number}")


class Ticket:
    def __init__(self, vehicle_number, vehicle_type, spot_id, ticket_id=None):
        self.vehicle_number = vehicle_number
        self.spot_id = spot_id
        self.vehicle_type = vehicle_type
        self.ticket_id = ticket_id or str(uuid.uuid4())
        self.entry_time = datetime.datetime.utcnow()
        self.exit_time = None

    def get_ticket_id(self):
        return self.ticket_id

    def get_vehicle_number(self):
        return self.vehicle_number

    def get_spot_id(self):
        return self.spot_id

    def set_exit_time(self):
        self.exit_time = datetime.datetime.utcnow()

    def printer(self):
        return {
            "ticketId": self.ticket_id,
            "vehicleNumber": self.vehicle_number,
            "spotId": self.spot_id,
            "vehicleType": self.vehicle_type,
            "entryTime": self.entry_time,
            "exitTime": self.exit_time
        }


class SearchManager:
    def __init__(self):
        self.by_vehicle_number = {}
        self.by_ticket = {}
        self.by_spot = {}

    def ticket_search(self, ticket_id):
        return self.by_ticket.get(ticket_id)

    def vehicle_search(self, vehicle_number):
        return self.by_vehicle_number.get(vehicle_number)

    def spot_search(self, spot_id):
        return self.by_spot.get(spot_id)

    def index(self, ticket):
        self.by_ticket[ticket.get_ticket_id()] = ticket
        self.by_vehicle_number[ticket.get_vehicle_number()] = ticket
        self.by_spot[ticket.get_spot_id()] = ticket

    def un_index(self, ticket):
        self.by_ticket.pop(ticket.get_ticket_id(), None)
        self.by_vehicle_number.pop(ticket.get_vehicle_number(), None)
        self.by_spot.pop(ticket.get_spot_id(), None)


# ------------------ Strategy Pattern ------------------

class ParkingStrategy(ABC):
    @abstractmethod
    def find_spot(self, parking_lot, vehicle_type):
        """Return a ParkingSpot or None."""
        pass


class NearestStrategy(ParkingStrategy):
    """
    Pick the first valid spot in floor -> row -> column order.
    Uses the lot's insertion order (configured FRC), and checks type & availability.
    """
    def find_spot(self, parking_lot, vehicle_type):
        for spot in parking_lot.iter_spots_frc():
            if spot.is_parking_available() and spot.vehicle_type == vehicle_type:
                return spot
        return None


class MostFreeFloorStrategy(ParkingStrategy):
    """
    Pick the floor having the MOST free spots for the given vehicle type.
    Tie-breaker: lower floor id.
    Then pick the nearest (row-major) spot on that floor.
    """
    def find_spot(self, parking_lot, vehicle_type):
        best_floor = None
        best_count = -1
        for floor_id in parking_lot.floor_spots.keys():
            cnt = parking_lot.floor_free_count[floor_id][vehicle_type]
            if cnt > best_count or (cnt == best_count and (best_floor is None or floor_id < best_floor)):
                best_floor, best_count = floor_id, cnt

        if best_floor is None or best_count <= 0:
            return None

        for spot in parking_lot.iter_floor_spots(best_floor):
            if spot.is_parking_available() and spot.vehicle_type == vehicle_type:
                return spot
        return None


# ------------------ Parking Lot ------------------

class ParkingLot:
    """
    floor_list format:
      3D list of strings "vehicleType-canPark" e.g. "4-1", "2-0"
      - vehicleType in {"2","4"}
      - canPark in {"0","1"}  (0 => inactive/blocked; 1 => available initially)
    """
    def __init__(self, floor_list):
        self.parking_spots = {}  # spot_id -> ParkingSpot
        self.floor_spots = defaultdict(list)  # floor_id -> [ParkingSpot in row-major]
        self.tickets = []
        self.search_manager = SearchManager()
        self.floor_free_count = defaultdict(lambda: defaultdict(int))  # floor -> {2: count, 4: count}
        self._configure(floor_list)

    def _configure(self, floor_list):
        for f, fl in enumerate(floor_list):
            for r, fr in enumerate(fl):
                for c, fc in enumerate(fr):
                    vehicle_type_str, can_park_str = fc.split('-')
                    vehicle_type = int(vehicle_type_str)
                    can_park = bool(int(can_park_str))

                    spot = ParkingSpot(f, r, c, vehicle_type, can_park)
                    sid = spot.get_spot_id()
                    self.parking_spots[sid] = spot
                    self.floor_spots[f].append(spot)
                    if can_park and vehicle_type in (2, 4):
                        self.floor_free_count[f][vehicle_type] += 1

    # ---- Iteration helpers (deterministic nearest: floor->row->col) ----
    def iter_spots_frc(self):
        for f in sorted(self.floor_spots.keys()):
            # already stored in row-major order in _configure
            for spot in self.floor_spots[f]:
                yield spot

    def iter_floor_spots(self, floor_id):
        for spot in self.floor_spots[floor_id]:
            yield spot

    # ---- API ----
    def park(self, vehicle_type, vehicle_number, ticket_id=None, strategy: ParkingStrategy = None):
        if strategy is None:
            strategy = NearestStrategy()

        spot = strategy.find_spot(self, vehicle_type)
        if not spot:
            return None

        if spot.park(vehicle_type, vehicle_number):
            # update free count
            self.floor_free_count[spot.floor][vehicle_type] -= 1
            # create and index ticket
            ticket = Ticket(vehicle_number, vehicle_type, spot.get_spot_id(), ticket_id)
            self.tickets.append(ticket)
            self.search_manager.index(ticket)
            return ticket.printer()
        return None

    def un_park(self, ticket_id=None, spot_id=None, vehicle_number=None):
        try:
            if ticket_id:
                ticket = self.search_manager.ticket_search(ticket_id)
            elif vehicle_number:
                ticket = self.search_manager.vehicle_search(vehicle_number)
            elif spot_id:
                ticket = self.search_manager.spot_search(spot_id)
            else:
                raise AttributeError("Search Not supported")

            if not ticket:
                return 404

            sid = ticket.get_spot_id()
            spot = self.parking_spots[sid]
            spot.remove_parking()
            self.floor_free_count[spot.floor][spot.vehicle_type] += 1
            self.search_manager.un_index(ticket)
            ticket.set_exit_time()
            return 201
        except KeyError:
            return 404

    def search(self, query):
        """
        Search by ticketId OR vehicleNumber OR spotId.
        Returns ticket dict or None.
        """
        t = (self.search_manager.ticket_search(query)
             or self.search_manager.vehicle_search(query)
             or self.search_manager.spot_search(query))
        return t.printer() if t else None

    def get_free_spots_count(self, floor, vehicle_type):
        return self.floor_free_count[floor][vehicle_type]

    def display(self):
        for _, spot in self.parking_spots.items():
            spot.display()


# ------------------ Demo ------------------

if __name__ == "__main__":
    # Two floors, simple layout using "type-canPark" format where 0=blocked
    layout = [
        [
            ["2-1", "4-1", "2-1", "2-0"],
            ["2-1", "4-1", "2-1", "4-1"]
        ],
        [
            ["4-1", "2-1", "4-1", "2-1"],
            ["4-1", "4-1", "2-1", "2-1"]
        ]
    ]

    lot = ParkingLot(layout)

    # Strategies
    nearest = NearestStrategy()
    most_free = MostFreeFloorStrategy()

    # Park some vehicles
    t1 = lot.park(2, "KA01AA1111", strategy=nearest)
    print("Park result:", t1)

    t2 = lot.park(4, "KA01BB2222", strategy=nearest)
    print("Park result:", t2)

    t3 = lot.park(4, "KA01CC3333", strategy=most_free)
    print("Park result:", t3)

    # Search by different keys
    print("Search by ticket:", lot.search(t1["ticketId"]))
    print("Search by vehicle:", lot.search("KA01BB2222"))
    print("Search by spot:", lot.search(t3["spotId"]))

    # Free counts
    print("Free 2W on floor 0:", lot.get_free_spots_count(0, 2))
    print("Free 4W on floor 1:", lot.get_free_spots_count(1, 4))

    # Un-park by ticket
    print("Un-park status:", lot.un_park(ticket_id=t1["ticketId"]))
    print("Free 2W on floor 0 (after):", lot.get_free_spots_count(0, 2))
