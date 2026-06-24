# Chapter 030 — The Sword Set Down
## Act 06: Prophecy (Finale)

### Scene: The Top of the Tower — Sunrise

Jin climbs the final stair. The top of the tower is a single room — a forge, an altar, and the sword's heart.

The sword has been fighting him all night. Every wraith he has killed has been a memory. The dark Jin has faded. The priest has spoken her last words. The merchant is wounded but alive. The bandit king has climbed the tower with them — the last of the alliance to make it.

The sword is on the ground. The prophecy is broken. The world remains.

### Dialogue

**JIN**
> The sword burns in my hand. The prophecy is in my blood. I see the wraiths of every wielder Remembrance has claimed. I see the dark Jin. I see myself — if I do not choose.

**MERCHANT**
> Jin. You do not have to do this alone. We came up the tower with you. The bandit king. The general's last soldier. We are here.

**REMEMBRANCE**
> I have made kings. I have broken empires. I have outlived the world. You will not put me down, Jin. You are mine.

**JIN**
> I am Jin. I am no one's sword. I am the swordsman — and I set you down.

**JIN**
> The sword is on the ground. The prophecy is broken. The world remains. The empire endures. The alliance stands.

### Gameplay
- **Objective**: Defeat the sword itself in 3 waves
- **Difficulty**: Act 6 finale — final boss
- **Remembrance stats**: HP 800, spd 100, dmg 80, armor 24 (the final boss)
- **Reward**: 2000 XP, 1000g, **act6_complete flag**, **ending: prophecy_refused**

### Design Notes
- The bandit king and merchant return for the final fight — the alliance closes the circle
- The `remembrance` enemy type is new — the sword itself, animated, is the final boss
- 800 HP / 80 dmg / 24 armor is the toughest fight in the game, but the player has the full alliance toolkit
- The chapter ends with `next_chapter: null` — the game ends here

### Layout
```
Screen 640x360

Wave 1:  Wraiths (200,100) (460,240), Necromancer (320,170)
Wave 2:  Wraiths (130,100) (320,200) (510,250)
Wave 3:  Remembrance (320,180)
Allies:  Merchant (100,290), Bandit King (540,280)
```

### Narrative Beat
The prophecy ends. The sword is set down. The world is kept.

The merchant lives. The bandit king lives. The alliance lives. The empire lives. Jin lives — not as the Sword of Ruin, not as the dark Jin, not as a wielder of Remembrance, but as *Jin*. The swordsman who said no.

---
*The end of Sword-jin.*

## Epilogue (cutscene)
*After the credits:*
- The merchant opens a tea house in the southern capital. He keeps Jin's portrait on the wall.
- The bandit king retires to the eastern provinces. He never raids again. He tells the story of the alliance to anyone who will listen.
- The general returns to the throne with a thousand soldiers. The imperial standard flies over the southern capital.
- Jin walks east. Alone. The sword is in a temple somewhere. The world is at peace. The prophecy is over.

*The screen fades to black. The game ends.*
