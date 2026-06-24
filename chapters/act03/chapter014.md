# Chapter 014 — The Fang Priest
## Act 03: Betrayal (Mid-Act Boss)

### Scene: The Crimson Chapel — Storm-Swept

The chapel is a black tower of red stone, set into the cliff face where the eastern road meets the river. Inside, the air is thick with incense and the sound of chanting. The Fang's priest stands at the altar, wraiths orbiting her like a slowed constellation.

She has been waiting for Jin. She has *prophecy* waiting for Jin.

### Dialogue

**PRIEST**
> So. The Sword of Ruin stands before me. I had hoped the wraiths would greet you, but you cut through them as the prophecy said you would.

**JIN**
> Prophecy. The Fang's not just a cult — you've been expecting me.

**PRIEST**
> Every Fang priest learns your name. The wraiths you killed were the ones I bound. The wraith you ARE is the one the prophecy reserves.

**JIN**
> The choir scatters when the priest dies. Hold the line — Spirit Edge cuts through their binding.

**PRIEST**
> The Fang does not end with me. But the eastern roads... yes. You can have those.

**JIN**
> The priest is dead. The Fang's eastern network is broken. But the prophecy she spoke — I need answers, and there's only one place left to look.

### Gameplay

- **Objective**: Defeat the Crimson Fang's priest (3 waves: guards → wraith choir → priest + wraith lieutenants)
- **Difficulty**: Act 3 mid-boss — the hardest single fight until the Act 3 finale
- **Priest stats**: HP 160, spd 50, dmg 18 (caster boss, slow but durable)
- **Wraith lieutenants**: HP 100, spd 80, dmg 32 (highest damage wraiths in the game)
- **Reward**: **Spirit Edge Duality** (legendary-rarity hybrid weapon — sword + wraith blade), 360 XP, 130g

### Design Notes
- **Wave 1 priority**: Shaman again. Same aura, same lesson. If the player hasn't learned to kill the shaman first by now, the rest of the chapter punishes them.
- **Wave 2 (wraith-only)**: Tests whether the player can handle sustained wraith pressure without backup. Spirit Edge mandatory.
- **Wave 3 (boss)**: The priest is the actual boss. Two wraith lieutenants stay close to her. Killing the lieutenants first removes the damage pressure but lets the priest debuff more. Killing the priest first ends the buffs but the lieutenants survive at full HP. The player picks the order.
- **"Spirit Edge Duality"** is a placeholder legendary reward — implementation pending in `WEAPON_STATS`. The reward is real (unlock entry added to chapter); the stats are open for the next design pass.

### Layout
```
Screen 640x360

Wave 1:  Assassins (130,90) (510,250) flank, Shaman (340,200) rear-support
Wave 2:  Wraith triangle (200,100) (470,130) (330,270) — pincer
Wave 3:  Necromancer-priest (320,170) center, Wraith lieutenants (200,110) (460,240) flanking
```

### Narrative Beat
The priest names Jin. The prophecy reserves him. He is no longer a rusted-blade survivor; he is a *target* of the Fang's most ancient doctrine. The wraiths he's been killing were sent to test him. The priest was the first to *fail* in that test.

Act 3's betrayal is now complete: the Fang knew he was coming. They prepared. They *need* him alive. The questions are why, and what the prophecy says he'll become.

The eastern roads open. South lies the Crimson Fang's capital — and the only person who can answer the prophecy question is the Fang's *master*, who lives there. Act 3 ends not with victory, but with direction.

---
*Next: Chapter 015 — The Road South (Act 3 finale, Act 4 bridge)*
