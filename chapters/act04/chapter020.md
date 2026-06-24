# Chapter 020 — The Capital's Shadow
## Act 04: Alliance (Finale)

### Scene: The Southern Capital's Outer Wall — Storm

The alliance reaches the southern capital at sunset. The outer fortress is a black wall of red stone, defended by golems and Fang elites. The inner city rises behind it — a thousand rooftops, a single dark tower at the center, and the master of the Crimson Fang within.

The imperial court's full army is two days behind. Jin has one day to breach the outer wall.

### Dialogue

**JIN**
> The southern capital. Tomorrow we breach the inner wall. Tonight — we rest. The Fang's master is in there, and I intend to meet him.

**WARDEN**
> Jin. The throne's full army is on the road. You'll have a thousand swords by the inner wall. Make the breach count.

**JIN**
> Two golems. The Fang's pulling out everything. Rally Cry before the second wave — the alliance needs to be at full strength for what's coming.

**NECROMANCER**
> You have come so far. But beyond me is the master — and he does not die as I do.

**JIN**
> The outer fortress is ours. The inner wall is broken. The throne's army arrives at dawn. Act Four ends here — the war begins in earnest.

### Gameplay
- **Objective**: Breach the outer wall in a 3-wave siege
- **Difficulty**: Act 4 finale — full alliance vs. full Fang garrison
- **Wave 3 (inner master)**: Necromancer + 2 wraiths + shaman (the Fang's inner court)
- **Reward**: 600 XP, 250g, **act4_complete flag**

### Design Notes
- This is the alliance's first *siege*. 2 golems in wave 1 is the kind of stat pressure the alliance was built for
- The "inner master" necromancer is the same enemy type as the ch012 boss, but at HP 200 — the same enemy, scaled up
- The warden's "thousand swords" line sets up Act 5's "War" theme: army-vs-army

### Layout
```
Screen 640x360

Wave 1:  Golems (180,100) (470,250), Bandit (320,180)
Wave 2:  Wraiths (200,100) (460,230), Assassin (330,270)
Wave 3:  Necromancer (320,170), Wraiths (200,110) (460,240), Shaman (100,280)
Allies:  Merchant (100,290), Soldiers (80,200) (560,200) (540,280), Bandit King (540,130)
```

### Narrative Beat
Act 4 ends with the alliance standing at the breach. The imperial army is two days out. The Fang's master is in the inner city. The prophecy — the reason the priest named Jin — has not been answered, only delayed.

Act 5 (War) opens with the imperial army arriving, the alliance becoming an army proper, and the siege of the southern capital in earnest. The Fang's master waits at the dark tower.

---
*Next: Chapter 021 — The Siege Begins (Act 5: War opens. Army-vs-army.)*
