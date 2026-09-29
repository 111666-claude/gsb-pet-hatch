"""宠物孵化：时长、加速道具与领取幂等。"""


class HatchError(ValueError):
    """孵化操作不合法，携带蛋的编号。"""

    def __init__(self, egg_id, message):
        super().__init__(message)
        self.egg_id = egg_id
        self.message = message


class Egg:
    """一枚蛋。"""

    __slots__ = ("egg_id", "start", "duration", "boost_used", "claimed")

    def __init__(self, egg_id, start, duration):
        self.egg_id = egg_id
        self.start = start
        self.duration = duration
        self.boost_used = False
        self.claimed = False


def progress(egg, now):
    """孵化进度（0..1），加速道具的减免通过 start 前移体现。"""
    elapsed = now - egg.start
    if elapsed < 0:
        elapsed = 0
    ratio = elapsed / egg.duration
    return ratio if ratio < 1 else 1.0


def boost(egg, amount):
    """使用加速道具：每枚蛋只能用一次，把 start 前移以真实缩短所需时长。"""
    if egg.boost_used:
        raise HatchError(egg.egg_id, "boost already used for egg %r" % (egg.egg_id,))
    egg.boost_used = True
    egg.start -= amount
    return egg


def claim(egg, now):
    """领取宠物：时长没到或已领取都返回 HatchError，成功只发生一次。"""
    if egg.claimed:
        raise HatchError(egg.egg_id, "egg %r already claimed" % (egg.egg_id,))
    if now - egg.start < egg.duration:
        raise HatchError(egg.egg_id, "egg %r not ready" % (egg.egg_id,))
    egg.claimed = True
    return True
