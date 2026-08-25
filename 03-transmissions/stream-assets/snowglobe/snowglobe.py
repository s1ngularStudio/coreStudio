import os
import random
import math

import py5

WIDTH = 1080
HEIGHT = 1920
FPS = 60

CHROMA_KEY = (0, 255, 0)
# No glass box is drawn -- this is a transparent overlay composited (via chroma key) on top
# of the OBS bookshelf/icy-landscape background image. BOX_MARGIN only keeps flakes and the
# bear off the very edge of frame; it isn't a visible container anymore.
BOX_MARGIN = 60

MAX_PARTICLES = 420

# Parallax bands, back to front. Far flakes are smaller, dimmer, slower, and sway less --
# near flakes are the opposite -- so a static camera reads depth from motion alone.
DEPTH_LAYERS = [
    {"scale": 0.5, "speed_mul": 0.5, "sway_mul": 0.6, "alpha": 130},
    {"scale": 1.0, "speed_mul": 1.0, "sway_mul": 1.0, "alpha": 210},
    {"scale": 2.1, "speed_mul": 1.7, "sway_mul": 1.4, "alpha": 255},
]
LAYER_WEIGHTS = [0.45, 0.35, 0.20]  # denser far layer, sparser near layer -- natural falloff

# Four intensities, off is a fifth "do nothing" state. "density" gates what fraction of
# MAX_PARTICLES are active (fixed per-flake threshold, so the active subset doesn't
# flicker); "wind" is the gust system's peak horizontal push (see update_wind_gust() --
# actual direction/strength varies over time, it isn't a constant push); "turbulence" is
# per-frame random horizontal jitter; "vertical_turbulence" adds chaotic up/down jitter on
# top of the steady fall, for the churning/swirling look at heavy/storm. "gust_range" is
# the (min, max) direction multiplier the wind retargets to -- light stays mostly one
# direction, storm's range spans fully negative to positive so it reverses outright.
# "gust_interval" is how often (seconds, min/max) a new target gets picked; "gust_lerp" is
# how fast current direction chases that target -- storm's low interval + high lerp is what
# makes it feel like it's "coming from everywhere" rather than one steady blow.
#
# No full-frame "whiteout" tint -- an earlier version blended translucent white over the
# whole canvas at heavy/storm to fake reduced visibility, but this canvas doubles as the
# chroma-key background: blending white into the pure-green areas shifts their color away
# from the key color, so OBS's chroma key filter stops keying them out and the green shows
# through as a visible wash instead of staying transparent (confirmed live 2026-08-24, "the
# green screen in the back showed" at !snow heavy). Reduced visibility at heavy/storm comes
# only from density/speed/wind/turbulence now -- real occlusion from opaque flakes, which
# doesn't touch the key-color pixels those flakes aren't covering.
SNOW_LEVELS = {
    "light": {
        "density": 0.45, "speed_mul": 1.3, "wind": 20, "turbulence": 10,
        "vertical_turbulence": 0, "gust_range": (0.3, 1.0),
        "gust_interval": (3.0, 6.0), "gust_lerp": 1.0,
    },
    "medium": {
        "density": 0.7, "speed_mul": 1.9, "wind": 55, "turbulence": 25,
        "vertical_turbulence": 5, "gust_range": (-0.3, 1.0),
        "gust_interval": (2.0, 4.0), "gust_lerp": 1.5,
    },
    "heavy": {
        "density": 0.9, "speed_mul": 2.6, "wind": 120, "turbulence": 55,
        "vertical_turbulence": 20, "gust_range": (-0.8, 1.0),
        "gust_interval": (0.8, 2.0), "gust_lerp": 2.5,
    },
    "storm": {
        "density": 1.0, "speed_mul": 3.6, "wind": 260, "turbulence": 130,
        "vertical_turbulence": 60, "gust_range": (-1.0, 1.0),
        "gust_interval": (0.25, 0.8), "gust_lerp": 4.0,
    },
}

SNOW_STATE_PATH = os.path.join(os.path.dirname(__file__), "snow_state.txt")
POLAR_BEAR_STATE_PATH = os.path.join(os.path.dirname(__file__), "polar_bear_state.txt")


class SnowState:
    """All snow-related mutable state in one named place, rather than loose module
    globals -- includes the gust direction, since it's shared across every flake (they
    should all feel the same instantaneous wind, not drift independently).
    """

    def __init__(self):
        self.level = "off"
        self.last_mtime = 0.0
        self.wind_dir = 0.0
        self.wind_dir_target = 0.0
        self.wind_retarget_timer = 0.0


class PolarBearState:
    def __init__(self):
        self.on = False
        self.last_mtime = 0.0


particles = []
snow_state = SnowState()
polar_bear_state = PolarBearState()


class Flake:
    __slots__ = (
        "box_x", "box_w", "box_bottom", "layer", "active_threshold",
        "x", "y", "size", "speed", "sway_phase", "sway_speed", "sway_amp", "alpha",
    )

    def __init__(self, box_x, box_w, box_bottom):
        self.box_x = box_x
        self.box_w = box_w
        self.box_bottom = box_bottom
        self.reset(top=False)

    def reset(self, top):
        self.layer = random.choices(range(len(DEPTH_LAYERS)), weights=LAYER_WEIGHTS)[0]
        band = DEPTH_LAYERS[self.layer]
        # Assigned independent of layer, so a low density (e.g. "light") still activates a
        # mix of far/mid/near flakes rather than only ever lighting up one depth band.
        self.active_threshold = random.random()
        self.x = random.uniform(self.box_x, self.box_x + self.box_w)
        self.y = random.uniform(-40, 0) if top else random.uniform(0, self.box_bottom)
        self.size = random.uniform(3, 7) * band["scale"]
        self.speed = random.uniform(45, 90) * band["speed_mul"]
        self.sway_phase = random.uniform(0, math.tau)
        self.sway_speed = random.uniform(0.6, 1.4)
        self.sway_amp = random.uniform(10, 26) * band["sway_mul"]
        self.alpha = band["alpha"] + random.uniform(-15, 15)

    def is_out_of_bounds(self):
        return self.y - self.size > self.box_bottom

    def update(self, dt, speed_mul, wind, turbulence, vertical_turbulence):
        self.y += self.speed * speed_mul * dt
        if vertical_turbulence:
            self.y += random.uniform(-vertical_turbulence, vertical_turbulence) * dt
        self.sway_phase += self.sway_speed * dt
        if wind or turbulence:
            self.x += wind * dt + random.uniform(-turbulence, turbulence) * dt
            # Wind/turbulence push sideways, but flakes stay inside the container -- clamp
            # to the walls rather than letting them exit off the sides (per Rodrigo
            # 2026-08-24: "the snow should stay in the container, not fly off the sides").
            self.x = min(max(self.x, self.box_x), self.box_x + self.box_w)

    def draw(self):
        sway = math.sin(self.sway_phase) * self.sway_amp
        py5.no_stroke()
        py5.fill(255, 255, 255, self.alpha)
        py5.circle(self.x + sway, self.y, self.size)


def settings():
    py5.size(WIDTH, HEIGHT)


def setup():
    py5.window_title("Snowglobe")
    py5.frame_rate(FPS)
    box_x, box_w, box_bottom = BOX_MARGIN, WIDTH - BOX_MARGIN * 2, HEIGHT - BOX_MARGIN
    for _ in range(MAX_PARTICLES):
        particles.append(Flake(box_x, box_w, box_bottom))


def check_snow():
    if not os.path.exists(SNOW_STATE_PATH):
        return
    mtime = os.path.getmtime(SNOW_STATE_PATH)
    if mtime <= snow_state.last_mtime:
        return
    snow_state.last_mtime = mtime
    with open(SNOW_STATE_PATH) as f:
        requested = f.read().strip().lower()
    if requested != "off" and requested not in SNOW_LEVELS:
        print(f"[WARN] Unknown snow level '{requested}', ignoring")
        return
    if requested != snow_state.level:
        snow_state.wind_retarget_timer = 0.0  # force an immediate gust pick for the new level
    snow_state.level = requested


def update_wind_gust(dt, level):
    """Shifts the shared wind direction toward a new random target every so often, at a
    level-dependent pace -- see the SNOW_LEVELS comment for what each gust_* key controls.
    """
    snow_state.wind_retarget_timer -= dt
    if snow_state.wind_retarget_timer <= 0:
        snow_state.wind_dir_target = random.uniform(*level["gust_range"])
        snow_state.wind_retarget_timer = random.uniform(*level["gust_interval"])
    snow_state.wind_dir += (
        (snow_state.wind_dir_target - snow_state.wind_dir) * min(1.0, level["gust_lerp"] * dt)
    )


def check_polar_bear():
    if not os.path.exists(POLAR_BEAR_STATE_PATH):
        return
    mtime = os.path.getmtime(POLAR_BEAR_STATE_PATH)
    if mtime <= polar_bear_state.last_mtime:
        return
    polar_bear_state.last_mtime = mtime
    with open(POLAR_BEAR_STATE_PATH) as f:
        polar_bear_state.on = f.read().strip().lower() == "on"


# !polarBear on/off toggles polar_bear_state.on (see check_polar_bear() above) but nothing
# draws it yet -- the character is still being designed. Once real art exists, draw it
# here when polar_bear_state.on is True, before the snow loop below, so falling flakes
# still pass in front of it.


def draw():
    check_snow()
    check_polar_bear()
    dt = 1.0 / FPS

    py5.background(*CHROMA_KEY)

    if snow_state.level != "off":
        level = SNOW_LEVELS[snow_state.level]
        update_wind_gust(dt, level)
        effective_wind = level["wind"] * snow_state.wind_dir
        for flake in sorted(particles, key=lambda f: f.layer):
            if flake.active_threshold > level["density"]:
                continue
            flake.update(
                dt, level["speed_mul"], effective_wind,
                level["turbulence"], level["vertical_turbulence"],
            )
            if flake.is_out_of_bounds():
                flake.reset(top=True)
            flake.draw()


py5.run_sketch()
