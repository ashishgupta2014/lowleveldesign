import datetime
import uuid


class ParkingSpot:

    def __init__(self, floor, row, column, vehicle_type, can_park=True, vehicle_number=None):
        self.floor = floor
        self.row = row
        self.column = column
        self.vehicle_type = vehicle_type
        self.vehicle_number = vehicle_number
        self.can_park = can_park

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
            "exitTime": self.exit_time}


class SearchManager:

    def __init__(self):
        self.by_vehicle_number = {}
        self.by_ticket = {}
        self.by_spot = {}

    def ticket_search(self, ticket_id):
        return self.by_ticket[ticket_id]

    def vehicle_search(self, vehicle_number):
        return self.by_vehicle_number[vehicle_number]

    def spot_search(self, spot_id):
        return self.by_spot[spot_id]

    def index(self, ticket):
        self.by_ticket[ticket.get_ticket_id()] = ticket
        self.by_vehicle_number[ticket.get_vehicle_number()] = ticket
        self.by_spot[ticket.get_spot_id()] = ticket

    def un_index(self, ticket):
        self.by_ticket[ticket.get_ticket_id()] = None
        self.by_vehicle_number[ticket.get_vehicle_number()] = None
        self.by_spot[ticket.get_spot_id()] = None


class ParkingLot:

    def __init__(self, floor_list):
        self.parking_spots = {}
        self.tickets = []
        self.search_manager = SearchManager()
        self._configure(floor_list)

    def _configure(self, floor_list):
        for f, fl in enumerate(floor_list):
            for r, fr in enumerate(fl):
                for c, fc in enumerate(fr):
                    if fc == "4-0":
                        print("ooo")
                    vehicle_type, can_park = fc.split('-')
                    can_park = bool(int(can_park))
                    parking_spot = ParkingSpot(f, r, c, vehicle_type, can_park)
                    self.parking_spots[parking_spot.get_spot_id()] = parking_spot

    def park(self, vehicle_type, vehicle_number, ticket_id=None):
        for _, spot in self.parking_spots.items():
            if spot.park(vehicle_type, vehicle_number):
                ticket = Ticket(vehicle_number, vehicle_type, spot.get_spot_id(), ticket_id)
                self.tickets.append(ticket)
                self.search_manager.index(ticket)
                return ticket.printer()

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
            spot_id = ticket.get_spot_id()
            spot = self.parking_spots[spot_id]
            spot.remove_parking()
            self.search_manager.un_index(ticket)
            return 201
        except KeyError:
            return 404

    def display(self):
        for _, spot in self.parking_spots.items():
            spot.display()


if __name__ == "__main__":
    parking_0 = [[
        ["4-1", "4-1", "2-1", "2-0"],
        ["2-1", "4-1", "2-1", "2-1"],
        ["4-0", "2-1", "4-0", "2-1"],
        ["4-1", "4-1", "4-1", "2-1"]]]
    parking_lot_1 = ParkingLot(parking_0)
    print(parking_lot_1.display())
    parking_1 = [[
        ["2-1", "4-1", "2-1", "4-1"],
        ["2-1", "2-1", "4-1", "4-1"]
    ],
        [
            ["2-1", "2-1", "4-1", "2-1"],
            ["4-1", "4-1", "2-1", "2-1"]
        ]]
    parking_lot_2 = ParkingLot(parking_1)
    print(parking_lot_2.display())
