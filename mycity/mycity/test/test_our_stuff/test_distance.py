import unittest
from abc import ABC, abstractmethod


class Distance(ABC):
    pass

    @property
    @abstractmethod
    def value(self):
        raise NotImplementedError


class Mile(Distance):
    def __init__(self, value: float):
        self._value = value

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return f'Mile({self.value})'


class Kilometer(Distance):
    def __init__(self, value: float):
        self._value = value

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return f'Kilometer({self.value})'


class DistanceConverter(object):
    conversions = {
        Mile: {Mile: 1.0, Kilometer: 0.621371},
        Kilometer: {Mile: 1.60934, Kilometer: 1.0}
    }

    def __init__(self, distance: Distance):
        self.distance = distance
        self._conversion_dict = self._get_conversion_dict()

    def _get_conversion_dict(self):
        for key, value in self.conversions.items():
            if isinstance(self.distance, key):
                return value
        raise ValueError(f'No conversions information found for {self.distance.__class__}')

    def convert_to(self, new_type):
        try:
            return new_type(self.distance.value * self._conversion_dict[new_type])
        except KeyError:
            raise ValueError(f'no conversion information found between {self.distance.__class__} and {new_type}')


class TestDistance(unittest.TestCase):
    def test_raises_not_implemented(self):
        class DummyDistance(Distance):
            @property
            def value(self):
                return super(DummyDistance, self).value

        test = DummyDistance()
        self.assertRaises(NotImplementedError, getattr, test, 'value')


class TestMile(unittest.TestCase):
    def test_init(self):
        value = 3.0
        distance = Mile(value)
        self.assertEqual(distance.value, value)

    def test_is_subclass_of_Distance(self):
        value = 3.0
        distance = Mile(value)
        self.assertIsInstance(distance, Distance)


class TestKilometer(unittest.TestCase):
    def test_init(self):
        value = 3.0
        distance = Kilometer(value)
        self.assertEqual(distance.value, value)

    def test_is_subclass_of_Distance(self):
        value = 3.0
        distance = Kilometer(value)
        self.assertIsInstance(distance, Distance)


class TestDistanceConverter(unittest.TestCase):
    def test_init(self):
        distance = Mile(1.0)
        to_test = DistanceConverter(distance)
        self.assertEqual(to_test.distance, distance)

    def test_convert_Mile_to_Mile(self):
        distance = Mile(1.0)
        converter = DistanceConverter(distance)
        new_distance = converter.convert_to(Mile)
        self.assertEqual(distance.value, new_distance.value)
        self.assertIsInstance(new_distance, Mile)

    def test_convert_Kilometer_to_Kilometer(self):
        distance = Kilometer(1.0)
        converter = DistanceConverter(distance)
        new_distance = converter.convert_to(Kilometer)
        self.assertEqual(distance.value, new_distance.value)
        self.assertIsInstance(new_distance, Kilometer)

    def test_convert_Mile_to_Kilometer(self):
        mile_value = 1.0
        expected_kilometer_value = mile_value * 0.621371
        distance = Mile(mile_value)
        converter = DistanceConverter(distance)
        new_distance = converter.convert_to(Kilometer)
        self.assertEqual(expected_kilometer_value, new_distance.value)
        self.assertIsInstance(new_distance, Kilometer)

    def test_convert_Kilometer_to_Mile(self):
        kilometer_value = 1.0
        expected_mile_value = kilometer_value * 1.60934
        distance = Kilometer(kilometer_value)
        converter = DistanceConverter(distance)
        new_distance = converter.convert_to(Mile)
        self.assertEqual(expected_mile_value, new_distance.value)
        self.assertIsInstance(new_distance, Mile)

    def test_init_raises_value_error_if_not_in_converter(self):
        class DummyDistance(Distance):
            @property
            def value(self):
                return 1.0

        to_test = DummyDistance()
        self.assertRaises(ValueError, DistanceConverter, to_test)

    def test_convert_raises_value_error_if_not_in_converter(self):
        class DummyDistance(Distance):
            @property
            def value(self):
                return 1.0

        distance = Mile(1.0)
        converter = DistanceConverter(distance)
        self.assertRaises(ValueError, converter.convert_to, DummyDistance)
