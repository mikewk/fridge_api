from .storage import mutation as s
from .household import mutation as h
from .auth import mutation as a
from .misc import mutation as m
from .fooditem import mutation as f
from .removal import mutation as r
from .user import mutation as u

mutations = [s, h, a, m, f, r, u]
