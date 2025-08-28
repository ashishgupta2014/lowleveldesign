from abc import ABC, abstractmethod


class SeatAllocationStrategy(ABC):
    @abstractmethod
    def allocate(self, show, tickets_count):
        pass


class ContiguousSeatStrategy(SeatAllocationStrategy):
    def allocate(self, show, tickets_count):
        rows, cols = len(show.seats), len(show.seats[0])
        for r in range(rows):
            for c in range(cols - tickets_count + 1):
                if all(not show.seats[r][c + k] for k in range(tickets_count)):
                    allocated = []
                    for k in range(tickets_count):
                        show.seats[r][c + k] = True
                        allocated.append(f"{r}-{c + k}")
                    show.free_count -= tickets_count
                    return allocated
        return []  # If contiguous not found


class BestAvailableSeatStrategy(SeatAllocationStrategy):
    def allocate(self, show, tickets_count):
        rows, cols = len(show.seats), len(show.seats[0])
        allocated = []
        for r in range(rows):
            for c in range(cols):
                if not show.seats[r][c]:
                    show.seats[r][c] = True
                    allocated.append(f"{r}-{c}")
                    if len(allocated) == tickets_count:
                        show.free_count -= tickets_count
                        return allocated
        return []


class Show:
    def __init__(self, show_id, movie_id, cinema_id, screen_idx, start_time, end_time, rows, cols):
        self.show_id = show_id
        self.movie_id = movie_id
        self.cinema_id = cinema_id
        self.screen_idx = screen_idx
        self.start_time = start_time
        self.end_time = end_time
        self.seats = [[False] * cols for _ in range(rows)]
        self.free_count = rows * cols

    def book_seats(self, ticket_id, tickets_count, strategies, bookings):
        if self.free_count < tickets_count:
            return []
        for strategy in strategies:
            allocated = strategy.allocate(self, tickets_count)
            if allocated:
                bookings[ticket_id] = {"showId": self.show_id, "seats": allocated}
                return allocated
        return []

    def cancel_seats(self, booking):
        for seat in booking["seats"]:
            r, c = map(int, seat.split("-"))
            self.seats[r][c] = False
        self.free_count += len(booking["seats"])


class Cinema:
    def __init__(self, cinema_id, city_id, screen_count, rows, cols):
        self.cinema_id = cinema_id
        self.city_id = city_id
        self.screens = {i: {"rows": rows, "cols": cols} for i in range(1, screen_count + 1)}


class BookMyShow:
    def __init__(self):
        self.cities = {}  # cityId -> set of cinemaIds
        self.cinemas = {}  # cinemaId -> Cinema
        self.shows = {}  # showId -> Show
        self.bookings = {}  # ticketId -> Booking
        # Strategy chain
        self.strategies = [ContiguousSeatStrategy(), BestAvailableSeatStrategy()]

    def add_cinema(self, cinema_id, city_id, screen_count, rows, cols):
        cinema = Cinema(cinema_id, city_id, screen_count, rows, cols)
        self.cinemas[cinema_id] = cinema
        self.cities.setdefault(city_id, set()).add(cinema_id)

    def add_show(self, show_id, movie_id, cinema_id, screen_index, start_time, end_time):
        cinema = self.cinemas.get(cinema_id)
        if not cinema or screen_index not in cinema.screens:
            return
        rows = cinema.screens[screen_index]["rows"]
        cols = cinema.screens[screen_index]["cols"]
        show = Show(show_id, movie_id, cinema_id, screen_index, start_time, end_time, rows, cols)
        self.shows[show_id] = show

    def book_ticket(self, ticket_id, show_id, tickets_count):
        show: Show = self.shows.get(show_id)
        if not show:
            return []
        return show.book_seats(ticket_id, tickets_count, self.strategies, self.bookings)

    def cancel_ticket(self, ticket_id):
        if ticket_id not in self.bookings:
            return False
        booking = self.bookings.pop(ticket_id)
        show = self.shows[booking["showId"]]
        show.cancel_seats(booking)
        return True

    def get_free_seats_count(self, show_id):
        return self.shows.get(show_id).free_count if show_id in self.shows else 0

    def list_cinemas(self, movie_id, city_id):
        result = []
        for cid in sorted(self.cities.get(city_id, [])):
            if any(sh.movie_id == movie_id and sh.cinema_id == cid for sh in self.shows.values()):
                result.append(cid)
        return result

    def list_shows(self, movie_id, cinema_id):
        filtered = [(sh.start_time, sid) for sid, sh in self.shows.items()
                    if sh.movie_id == movie_id and sh.cinema_id == cinema_id]
        filtered.sort(key=lambda x: (-x[0], x[1]))
        return [sid for _, sid in filtered]


if __name__ == "__main__":
    system = BookMyShow()

    # Step 1: Add Cinema
    system.add_cinema(cinema_id=101, city_id=1, screen_count=2, rows=3, cols=5)
    system.add_cinema(cinema_id=102, city_id=1, screen_count=1, rows=4, cols=4)

    # Step 2: Add Shows
    system.add_show(show_id=201, movie_id=301, cinema_id=101, screen_index=1, start_time=1600, end_time=1800)
    system.add_show(show_id=202, movie_id=301, cinema_id=101, screen_index=2, start_time=1830, end_time=2030)
    system.add_show(show_id=203, movie_id=302, cinema_id=102, screen_index=1, start_time=1700, end_time=1900)

    # Step 3: Book Tickets
    print("Booking Ticket 1:", system.book_ticket(ticket_id=401, show_id=201, tickets_count=3))
    print("Booking Ticket 2:", system.book_ticket(ticket_id=402, show_id=201, tickets_count=2))
    print("Booking Ticket 3 (fallback allocation):", system.book_ticket(ticket_id=403, show_id=201, tickets_count=4))

    # Step 4: Check Free Seats
    print("Free Seats in Show 201:", system.get_free_seats_count(201))

    # Step 5: Cancel Ticket
    print("Cancel Ticket 402:", system.cancel_ticket(402))
    print("Free Seats in Show 201 after cancel:", system.get_free_seats_count(201))

    # Step 6: List Cinemas for a Movie in City
    print("Cinemas in City 1 showing Movie 301:", system.list_cinemas(movie_id=301, city_id=1))

    # Step 7: List Shows in a Cinema for a Movie
    print("Shows in Cinema 101 for Movie 301:", system.list_shows(movie_id=301, cinema_id=101))

