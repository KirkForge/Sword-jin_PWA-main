# Chapter 025 — The Tower's Climb
## Act 05: War (Finale)

### Scene: The Dark Tower — Midnight

Jin climbs the tower alone. The alliance holds the third district. The general's army surrounds the city. The merchant, the bandit king, the imperial soldiers — all of them watch the tower's silhouette as Jin disappears through the door.

Three chambers. The outer is wraiths and assassins. The inner is the master's court — a necromancer, a golem of terrifying size, more wraiths. The final chamber is the master himself.

### Dialogue

**JIN**
> The door closes behind me. The alliance holds the third district. From here, I climb alone.

**MASTER**
> The Sword of Ruin. The priest told me about you. She said the prophecy named you. She died before she could tell me the rest.

**JIN**
> The prophecy is a lie. I am no one's sword. I am Jin, and I am here to end you.

**MASTER**
> Then end me, Sword. But know this — the prophecy was never about the Fang. It was about what comes after.

**JIN**
> The master falls. The tower crumbles. Act Five ends with the Fang broken — and the prophecy unanswered.

### Gameplay
- **Objective**: Defeat the master of the Crimson Fang in 3 chambers
- **Difficulty**: Act 5 finale — Jin alone, no allies
- **Master stats**: HP 600, spd 100, dmg 60, armor 20 (the most dangerous enemy in the game)
- **Reward**: 1500 XP, 600g, **act5_complete flag**

### Design Notes
- The first chapter with NO allies. Jin is on his own. The merchant can't help here. The bandit king can't help here. The general can't help here. This is the boss.
- The `master_fang` enemy type is new — must be added to the bestiary and the enemy scenes registry
- The master's dying line sets up Act 6's prophecy arc
- 600 HP is a stat-check: the player must have Spirit Edge + Rally Cry + the full Act 4 toolkit to win

### Narrative Beat
Act 5 ends with the master dying in his own tower. The Crimson Fang is broken. The southern capital is the throne's. But the prophecy — the reason the priest named Jin, the reason the Sword of Ruin was forged — remains unanswered.

Act 6 (Prophecy) opens with the question: *what comes after?*
