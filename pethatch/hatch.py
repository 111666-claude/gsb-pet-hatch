"""宠物孵化：时长、加速道具与领取幂等。

缺陷：时长没到也能领、领取不幂等、加速道具可以反复使用。
"""


class HatchError(ValueError):
    """输入不合法。缺陷：不带蛋的编号。"""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class Egg:
    """一枚蛋。"""

    def __init__(self, egg_id, start, duration):
        self.egg_id = egg_id
        self.start = start
        self.duration = duration
        self.boost_used = False
        self.claimed = False


def progress(egg, now):
    """孵化进度（0..1）。缺陷：加速道具的减免没算进去。"""
    elapsed = now - egg.start
    if elapsed < 0:
        elapsed = 0
    ratio = elapsed / egg.duration
    return ratio if ratio < 1 else 1.0


def boost(egg, amount):
    """使用加速道具。缺陷：可以重复使用多次。"""
    egg.start -= amount
    return egg


def claim(egg, now):
    """领取宠物。缺陷：不看进度、也不看是否已经领过。"""
    egg.claimed = True
    return True
