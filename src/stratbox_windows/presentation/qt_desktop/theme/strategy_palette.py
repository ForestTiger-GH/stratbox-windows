from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AvatarGradient:
    start: str
    end: str
    border: str
    text: str = '#F8FAFC'


_SYSTEM = AvatarGradient('#2F7681', '#4A90A4', '#8BB9C2')
_BACKGROUND = AvatarGradient('#49717B', '#5E8892', '#9FB8BE')
_AI = AvatarGradient('#6B5CA5', '#8B78C6', '#B4A8DB')

_USER_FAMILIES: tuple[AvatarGradient, ...] = (
    AvatarGradient('#2E7B83', '#4B98A2', '#9EC8CE'),
    AvatarGradient('#4B6FA5', '#638AC2', '#A8BEDF'),
    AvatarGradient('#3E8A68', '#58A47D', '#A7D2BC'),
    AvatarGradient('#7B6A4A', '#9D845E', '#D6C4A8'),
    AvatarGradient('#6F5D9B', '#8B77B9', '#C7BCDF'),
    AvatarGradient('#8A5F73', '#A87790', '#DDC2CC'),
    AvatarGradient('#3F748F', '#5C91AB', '#A9C8D8'),
    AvatarGradient('#577B6A', '#709785', '#B7D0C5'),
)


def _stable_index(key: str) -> int:
    return sum(ord(ch) for ch in key) % len(_USER_FAMILIES)


def resolve_avatar_gradient(*, actor_kind: str, palette_key: str) -> AvatarGradient:
    if palette_key == 'system' or actor_kind == 'system':
        return _SYSTEM
    if actor_kind == 'background' or palette_key.startswith('background:'):
        return _BACKGROUND
    if actor_kind == 'ai' or palette_key == 'ai':
        return _AI
    return _USER_FAMILIES[_stable_index(palette_key or actor_kind or 'user')]
