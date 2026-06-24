# Chapter 015 — The Road South
## Act 03: Betrayal (Finale)

### Scene: The Southern Pass — Dusk

The eastern roads are open. South lies the Fang's capital. Between Jin and that road: a narrow pass, the merchant caravan, and the last of the Fang's eastern warband.

The merchant is done running. They've traveled with Jin since the wagon fortress — healed his wounds, fed his spirit, kept him honest. Today they pick up a sword.

### Dialogue

**MERCHANT**
> Jin — the priest's dead but the Fang's still between us and the southern road. I'm not leaving you this time.

**JIN**
> Then we hold here. The caravan gets through or none of us do.

**MERCHANT**
> I'll patch whoever I can. Don't you dare die on me now.

**JIN**
> The shaman again. Same trick, same fix. Cut the head off first.

**MERCHANT**
> The road is clear. Jin — I'm coming with you. Whatever the Fang's planning down south, you shouldn't walk into it alone.

**JIN**
> Act Three ends here. The prophecy, the priest, the Fang's master — all of it lies south now. And for the first time, I won't be walking alone.

### Gameplay

- **Objective**: Hold the southern pass for 3 waves; the merchant caravan must reach the capital road
- **Difficulty**: Sustained Act 3 peak — wraiths + assassins + shaman, no breaks
- **Wraith stats**: HP 95-110, spd 80-85, dmg 30-34 (high-tier wraiths)
- **Assassin (wave 3)**: HP 80, spd 150, dmg 36 (fastest enemy in the game)
- **Allies**: 2 merchant allies (HP 100, heal_amount 15) — doubled up for the finale
- **Reward**: **400 XP + 150g + act3_complete flag** (no weapon — the alliance *is* the reward)

### Design Notes
- **Wave 1 (reprisal)**: bandits + assassin. The Fang's last mundane response. Players should feel this is "easy" by now.
- **Wave 2 (pursuit)**: wraiths + shaman. The lesson from ch012 returns — shaman first.
- **Wave 3 (vanguard)**: wraith + assassin. The two enemy types Act 3 introduced, now paired. Highest-damage wave in the act.
- **Two merchant allies**: doubles the heal throughput. Jin can survive mistakes.
- **act3_complete: true** in rewards mirrors the `act2_complete: true` flag in ch010. The victory screen will pick this up to show "Act 3 Complete."

### Layout
```
Screen 640x360

Wave 1:  Bandits (130,100) (510,250) flank, Assassin (340,80) center
Wave 2:  Wraiths (200,120) (470,230) flank, Shaman (330,280) rear
Wave 3:  Wraiths (180,110) (460,130) pincer, Assassin (320,260) rear-stab
Allies:  Merchants (320,180) (360,200) — center healing core
```

### Narrative Beat
The merchant's arc is the spine of the player-facing story. They appeared in ch005 as a vulnerable trader the player was sent to protect. Through ch009 (wagon fortress), they were a target. By ch015, they are a *combat ally* — picking up a sword because Jin can't carry the southern road alone.

The Crimson Fang's prophecy, the priest's death, the wraith plague — all of it was Act 3's test. Jin passed. The southern road opens.

Act 4 (Alliance) opens with the merchant formally joining the party, the gate warden offering the imperial seal as a second ally, and a small army of frontier fighters who have been waiting for someone to lead them south. The Fang's master waits at the capital.

---
*Next: Chapter 016 — The Imperial Seal (Act 4 opens. The party forms.)*
