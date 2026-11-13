import unittest
from tests import PluginTest
from plugins.cocktail import Cocktail


class CocktailTest(PluginTest):
    """Offline tests for the 'cocktail cookbook' plugin.

    The tests exercise input handling and validation only, so they do
    not require network access to thecocktaildb.com.
    """

    def setUp(self):
        self.test = self.load_plugin(Cocktail)
        self.test.ally = self.ally_api

    def test_ingredients_list_available(self):
        ingredients = self.test.ingredients
        self.assertTrue(len(ingredients) > 0)
        self.assertIn("Rum", ingredients)

    def test_is_out_of_range(self):
        upper = len(self.test.ingredients)
        self.assertTrue(self.test.is_out_of_range(0, upper))
        self.assertTrue(self.test.is_out_of_range(-10, upper))
        self.assertTrue(self.test.is_out_of_range(upper + 1, upper))
        self.assertFalse(self.test.is_out_of_range(1, upper))
        self.assertFalse(self.test.is_out_of_range(upper, upper))

    def test_is_exit_input(self):
        self.assertTrue(self.test.is_exit_input("exit"))
        self.assertTrue(self.test.is_exit_input("EXIT"))
        self.assertFalse(self.test.is_exit_input("5"))

    def test_get_input_valid(self):
        self.queue_input("3")
        self.assertEqual(self.test.get_input("Base Ingredient", 10), 3)

    def test_get_input_exit(self):
        self.queue_input("exit")
        self.assertEqual(self.test.get_input("Base Ingredient", 10), "exit")

    def test_get_input_out_of_range_then_valid(self):
        self.queue_input("700")
        self.queue_input("-10")
        self.queue_input("4")
        self.assertEqual(self.test.get_input("Base Ingredient", 10), 4)


if __name__ == '__main__':
    unittest.main()
