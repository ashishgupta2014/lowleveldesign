import unittest

from elevetor_system.elevtor_system import ElevatorSystem
from elevetor_system.left_states import IdleState, MovingUpState, MovingDownState


class TestElevatorSystem(unittest.TestCase):
    def setUp(self):
        self.system = ElevatorSystem()
        self.system.init(floors=10, lifts=2)  # 10 floors, 2 lifts

    def test_lift_assignment(self):
        lift_id = self.system.request_lift(0, 5)
        self.assertIn(lift_id, [0, 1], "Should assign one of the lifts")
        self.assertNotEqual(lift_id, -1, "Should not return -1 for first valid request")

    def test_lift_direction_up(self):
        lift_id = self.system.request_lift(0, 5)
        for _ in range(6):  # Enough ticks to move from 0 to 5
            self.system.tick()
        states = self.system.get_lift_states()
        self.assertTrue(states[lift_id].startswith("5-"), "Lift should reach 5th floor")

    def test_lift_becomes_idle_after_drop(self):
        lift_id = self.system.request_lift(1, 3)
        for _ in range(3):
            self.system.tick()
        self.system.tick()
        self.assertTrue(self.system.get_lift_states()[lift_id].endswith("I"), "Lift should be idle after task")

    def test_lift_direction_down(self):
        self.system.lifts[0].current_floor = 7  # Manually set
        self.system.lifts[1].current_floor = 0
        lift_id = self.system.request_lift(5, 2)
        self.assertEqual(lift_id, 0, "Lift 0 should be selected as it is above 5")
        for _ in range(6):
            self.system.tick()
        self.assertTrue(self.system.get_lift_states()[0].startswith("2-"), "Lift 0 should reach floor 2")

    def test_multiple_requests(self):
        self.system.request_lift(0, 5)
        self.system.request_lift(1, 6)
        for _ in range(13):
            self.system.tick()
        states = self.system.get_lift_states()
        # Check that both lifts have moved and are idle again
        self.assertTrue(all(s.endswith("I") for s in states), "All lifts should be idle after tasks")

    def test_get_lifts_stopping_on_floor(self):
        self.system.request_lift(0, 5)
        self.system.tick()
        result = self.system.get_lifts_stopping_on_floor(5, 'U')
        self.assertIn(0, result, "Lift 0 should stop at floor 5 in UP direction")

    def test_ineligible_lift(self):
        self.system.lifts[0].current_floor = 5
        self.system.lifts[0].change_state(MovingDownState())
        lift_id = self.system.request_lift(6, 8)
        self.assertEqual(lift_id, 1, "Lift 0 should be ineligible to go up from 6 while moving down")

    def test_idle_lift_assignment(self):
        self.system.lifts[0].current_floor = 2
        self.system.lifts[1].current_floor = 5
        self.system.lifts[0].change_state(IdleState())
        self.system.lifts[1].change_state(MovingUpState())

        lift_id = self.system.request_lift(2, 6)
        self.assertEqual(lift_id, 0, "Idle lift closer to request should be selected")


if __name__ == '__main__':
    unittest.main()
