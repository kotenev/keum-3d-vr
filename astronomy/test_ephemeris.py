import unittest
from datetime import datetime, timezone
from ephemeris import (
    observe, sun_equatorial, moon_equatorial, horizontal,
    horizon_events, internal_globe_point, STAR_RADIUS, EARTH_RADIUS
)
from math import sqrt

class AstronomyTests(unittest.TestCase):
    def setUp(self):
        self.t = datetime(2026,3,20,12,tzinfo=timezone.utc)

    def test_equinox_declination(self):
        _,dec = sun_equatorial(self.t)
        self.assertLess(abs(dec),1.0)

    def test_noon_at_greenwich_equinox(self):
        ra,dec = sun_equatorial(self.t)
        alt,_ = horizontal(ra,dec,self.t,0,0)
        self.assertGreater(alt,85)

    def test_night_opposite_longitude(self):
        ra,dec = sun_equatorial(self.t)
        day,_ = horizontal(ra,dec,self.t,0,0)
        night,_ = horizontal(ra,dec,self.t,0,180)
        self.assertGreater(day,85)
        self.assertLess(night,-85)

    def test_lunar_finite(self):
        ra,dec = moon_equatorial(self.t)
        self.assertTrue(0<=ra<360 and -90<=dec<=90)

    def test_internal_nested(self):
        r=internal_globe_point(32,75,10)
        self.assertAlmostEqual(sqrt(sum(x*x for x in r)),10,places=5)
        self.assertLess(STAR_RADIUS,EARTH_RADIUS)

    def test_sunrise_sunset(self):
        events=horizon_events(self.t,0,0)
        self.assertEqual(len(events),2)
        self.assertEqual({x["event"] for x in events},{"rise","set"})

    def test_timezone(self):
        o=observe(self.t,55.7558,37.6173,"Europe/Moscow")
        self.assertTrue(o["local_time"].endswith("+03:00"))
        self.assertTrue(0<=o["illumination"]<=1)

    def test_invalid_latitude(self):
        with self.assertRaises(ValueError):observe(self.t,95,0)

if __name__=="__main__":unittest.main()
