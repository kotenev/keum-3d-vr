#!/usr/bin/env python3
"""KEUM observational astronomy -> symbolic Concave Earth projection.

No geophysical claim is made for a hollow Earth. UTC input, WGS84-like
geodetic angles, simplified solar/lunar ephemerides, standard topocentric
horizontal coordinates, and deterministic internal-sphere mapping.

Solar position: low-precision NOAA-style mean elements (not JPL ephemeris).
Lunar position: truncated periodic terms, adequate for illustration only.
Rise/set: numerical horizon crossing with approximate atmospheric correction.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from math import asin, atan2, cos, degrees, floor, pi, radians, sin, sqrt, tan
from zoneinfo import ZoneInfo
import argparse
import json
import math

TAU = 2 * pi
EARTH_RADIUS = 29.0
STAR_RADIUS = 17.0
SUN_ORBIT_RADIUS = 9.69
MOON_ORBIT_RADIUS = 13.43


def wrap_deg(v: float) -> float:
    return v % 360.0


def julian_day(dt: datetime) -> float:
    if dt.tzinfo is None:
        raise ValueError("UTC-aware datetime required")
    dt = dt.astimezone(timezone.utc)
    return dt.timestamp() / 86400.0 + 2440587.5


def obliquity(T: float) -> float:
    return 23.439291 - 0.0130042 * T


def sun_equatorial(dt: datetime) -> tuple[float, float]:
    """Approximate geocentric apparent RA/Dec in degrees."""
    T = (julian_day(dt) - 2451545.0) / 36525
    L0 = wrap_deg(280.46646 + T * (36000.76983 + 0.0003032*T))
    M = radians(wrap_deg(357.52911 + T * (35999.05029 - 0.0001537*T)))
    C = (1.914602 - T*(0.004817+0.000014*T))*sin(M)
    C += (0.019993 - 0.000101*T)*sin(2*M) + 0.000289*sin(3*M)
    omega = radians(125.04 - 1934.136*T)
    lam = radians(L0 + C - 0.00569 - 0.00478*sin(omega))
    eps = radians(obliquity(T) + 0.00256*cos(omega))
    ra = atan2(cos(eps)*sin(lam), cos(lam))
    dec = asin(sin(eps)*sin(lam))
    return wrap_deg(degrees(ra)), degrees(dec)


def moon_equatorial(dt: datetime) -> tuple[float, float]:
    """Truncated geocentric lunar position, not suitable for precision eclipses."""
    D = julian_day(dt) - 2451545.0
    L = wrap_deg(218.316 + 13.176396*D)
    Mm = radians(wrap_deg(134.963 + 13.064993*D))
    Ms = radians(wrap_deg(357.529 + 0.98560028*D))
    F = radians(wrap_deg(93.272 + 13.229350*D))
    E = radians(wrap_deg(297.850 + 12.190749*D))
    lon = radians(L + 6.289*sin(Mm) + 1.274*sin(2*E-Mm)
                  + 0.658*sin(2*E) + 0.214*sin(2*Mm)
                  - 0.186*sin(Ms) - 0.114*sin(2*F))
    lat = radians(5.128*sin(F) + 0.280*sin(Mm+F)
                  + 0.277*sin(Mm-F) + 0.173*sin(2*E-F))
    eps = radians(obliquity(D/36525))
    x = cos(lat)*cos(lon)
    y = cos(lat)*sin(lon)*cos(eps) - sin(lat)*sin(eps)
    z = cos(lat)*sin(lon)*sin(eps) + sin(lat)*cos(eps)
    return wrap_deg(degrees(atan2(y,x))), degrees(asin(max(-1,min(1,z))))


def sidereal_deg(dt: datetime, longitude_deg: float) -> float:
    JD = julian_day(dt)
    T = (JD-2451545.0)/36525
    gmst = 280.46061837 + 360.98564736629*(JD-2451545.0)
    gmst += 0.000387933*T*T - T**3/38710000
    return wrap_deg(gmst + longitude_deg)


def horizontal(ra_deg: float, dec_deg: float, dt: datetime,
               lat_deg: float, lon_deg: float) -> tuple[float,float]:
    """Altitude, azimuth degrees; azimuth 0=N, 90=E."""
    lat,dec = radians(lat_deg),radians(dec_deg)
    H = radians((sidereal_deg(dt,lon_deg)-ra_deg+180)%360-180)
    alt = asin(max(-1,min(1,sin(lat)*sin(dec)+cos(lat)*cos(dec)*cos(H))))
    east = -cos(dec)*sin(H)
    north = sin(dec)*cos(lat)-cos(dec)*cos(H)*sin(lat)
    az = atan2(east,north)
    return degrees(alt),wrap_deg(degrees(az))


def local_direction(alt_deg: float, az_deg: float) -> tuple[float,float,float]:
    """3D ENU-like axes: x=east, y=up, z=north."""
    a,z = radians(alt_deg),radians(az_deg)
    return cos(a)*sin(z),sin(a),cos(a)*cos(z)


def internal_globe_point(alt_deg: float,az_deg: float,radius: float) -> tuple[float,float,float]:
    return tuple(round(radius*x,7) for x in local_direction(alt_deg,az_deg))


def daylight_fraction(dt: datetime,lat_deg: float,lon_deg: float) -> float:
    """Smooth day/night visual mask, not a radiative transfer solution."""
    ra,dec = sun_equatorial(dt)
    alt,_ = horizontal(ra,dec,dt,lat_deg,lon_deg)
    return max(0.0,min(1.0,(alt+6)/12))


def horizon_events(date_utc: datetime, lat_deg: float, lon_deg: float,
                   body: str = "sun", step_minutes: int = 10):
    """UTC rise/set by bisection. Approximate threshold, no terrain model."""
    if body not in ("sun","moon"): raise ValueError("body must be sun or moon")
    date_utc=date_utc.astimezone(timezone.utc).replace(hour=0,minute=0,second=0,microsecond=0)
    eq=sun_equatorial if body=="sun" else moon_equatorial
    threshold=-0.833 if body=="sun" else 0.125
    def f(t):
        ra,dec=eq(t)
        return horizontal(ra,dec,t,lat_deg,lon_deg)[0]-threshold
    result=[]
    a=date_utc;fa=f(a)
    for k in range(1,1440//step_minutes+1):
        b=date_utc+timedelta(minutes=k*step_minutes);fb=f(b)
        if (fa<0<=fb) or (fa>=0>fb):
            left,right=a,b
            for _ in range(24):
                mid=left+(right-left)/2
                if (f(mid)<0)==(fa<0):left=mid
                else:right=mid
            result.append({"event":"rise" if fa<0 else "set","utc":(left+(right-left)/2).isoformat()})
        a,fa=b,fb
    return result


@dataclass
class Observation:
    utc: str
    latitude: float
    longitude: float
    timezone: str
    sun_ra_deg: float
    sun_dec_deg: float
    sun_alt_deg: float
    sun_az_deg: float
    moon_ra_deg: float
    moon_dec_deg: float
    moon_alt_deg: float
    moon_az_deg: float
    illumination: float
    sun_inner_xyz: tuple
    moon_inner_xyz: tuple
    star_radius: float
    earth_shell_radius: float
    solar_events_utc: list


def observe(dt: datetime,lat_deg: float,lon_deg: float,tz: str="UTC") -> dict:
    if not -90<=lat_deg<=90 or not -180<=lon_deg<=180:
        raise ValueError("invalid geodetic coordinates")
    if dt.tzinfo is None:raise ValueError("datetime must be timezone-aware")
    ZoneInfo(tz)  # validate IANA zone name
    dt=dt.astimezone(timezone.utc)
    sr,sd=sun_equatorial(dt);mr,md=moon_equatorial(dt)
    sa,sz=horizontal(sr,sd,dt,lat_deg,lon_deg)
    ma,mz=horizontal(mr,md,dt,lat_deg,lon_deg)
    o=Observation(dt.isoformat(),lat_deg,lon_deg,tz,sr,sd,sa,sz,mr,md,ma,mz,
                  daylight_fraction(dt,lat_deg,lon_deg),
                  internal_globe_point(sa,sz,SUN_ORBIT_RADIUS),
                  internal_globe_point(ma,mz,MOON_ORBIT_RADIUS),
                  STAR_RADIUS,EARTH_RADIUS,
                  horizon_events(dt,lat_deg,lon_deg))
    result=asdict(o)
    result["local_time"]=dt.astimezone(ZoneInfo(tz)).isoformat()
    result["status"]="observational ephemeris projected into symbolic concave geometry"
    result["accuracy"]="approximate; no topocentric lunar parallax, refraction model or terrain"
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--utc",default="2026-11-11T12:00:00+00:00")
    p.add_argument("--lat",type=float,default=55.7558)
    p.add_argument("--lon",type=float,default=37.6173)
    p.add_argument("--tz",default="Europe/Moscow")
    p.add_argument("--output")
    a=p.parse_args()
    dt=datetime.fromisoformat(a.utc.replace("Z","+00:00"))
    data=observe(dt,a.lat,a.lon,a.tz)
    result=json.dumps(data,ensure_ascii=False,indent=2)
    if a.output:
        from pathlib import Path
        Path(a.output).write_text(result,encoding="utf-8")
    else:print(result)


if __name__=="__main__":main()
