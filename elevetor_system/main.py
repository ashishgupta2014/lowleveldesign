from elevetor_system.elevtor_system import ElevatorSystem

if __name__ == "__main__":
    system = ElevatorSystem()
    system.init(10, 3)  # 10 floors, 3 lifts

    print(system.requestLift(0, 5))  # e.g., assigns lift 0
    system.tick()
    system.tick()
    print(system.getLiftStates())  # e.g., ['2-U', '0-I', '0-I']
    print(system.getLiftsStoppingOnFloor(5, 'U'))  # e.g., [0]
    system.tick()
    system.tick()
    print(system.getLiftStates())