# Chapter 012 — Crimson's Hollow
## Act 03: Betrayal

### Scene: The Hollow — Midnight

A sunken chapel in a ravine, the air thick with the smell of incense and iron. Crimson Fang cultists chant in a circle around a wraith-bound altar. At the center: a necromancer in torn robes, hands raised, pulling at the air.

This is the source of the wraiths Jin has been fighting. Not random — summoned, bound, *fed* by the Fang.

### Dialogue

**NECROMANCER**
> You've come so far to die in my hollow, Sword of Ruin. The Fang made me what I am — and you will feed my choir.

**JIN**
> Kill the shaman first. Without her aura, the rest of them are just dead men walking.

**NECROMANCER**
> No — the binding! You cannot break what the Crimson Fang has forged!

**JIN**
> The hollow is silent. Whoever taught that necromancer the binding... that's who I need to find.

### Gameplay

- **Objective**: Defeat the necromancer and the bound wraith choir (3 waves)
- **Difficulty**: Mid-boss — kill the shaman in wave 1 to remove the buff aura, then focus necromancer in wave 2
- **Necromancer stats**: HP 100, spd 55, dmg 14 (low damage — wraiths do the killing)
- **Bound Wraith (wave 3)**: HP 120, spd 80, dmg 30 — life-drain attack, faster than field wraiths
- **Reward**: 280 XP + 90g (no weapon — wraith drop is a future chapter hook)

### Design Notes
- **Wave 1 priority**: Shaman buff aura +2 bandits. The shaman MUST die first to neutralize the buff. Wave 1 is a "do you understand the system?" test.
- **Wave 2 priority**: Necromancer. Wraiths do the killing but die fast. Necromancer is the threat-via-attrition source.
- **Wave 3 echo**: The bound wraith is the necromancer's strongest summon, set free when the master dies. Now it targets Jin. This is a stat-check using Spirit Edge.
- The "binding" dialogue trigger mirrors the betrayal theme — the Fang didn't just raise the dead, they *enslaved* the already-raised.

### Layout
```
Screen 640x360

Wave 1:  Bandits (150,100) (520,130) flank, Shaman (340,250) rear-support
Wave 2:  Wraiths (200,90) (480,250) surround, Necromancer (340,150) center
Wave 3:  Bound Wraith (320,180) — the boss echo
```

### Narrative Beat
The merchant's wagon fortress held. The capital gates are open. Jin has now killed the source of the wraith plague. But the necromancer's final words — "you cannot break what the Crimson Fang has forged" — imply a chain. Someone taught the necromancer. The Crimson Fang has a *priest*.

Act 3 is mid-arc. The next step isn't more cultists — it's whoever is giving the orders.

---
*Next: Chapter 013 — The Shattered Vow (Assassin + Shaman gauntlet)*
