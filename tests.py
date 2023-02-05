import unittest

import match_demo_with_game


class TestMatchDemoWithGameMethods(unittest.TestCase):
    def test_main(self):
        self.assertTrue(match_demo_with_game.main(verbose=True))


if __name__ == '__main__':
    unittest.main()
