MOD NAME: "Prioritized Kill Dev Tool"

GOAL: Replace the vanilla "Kill" dev tool so it only kills the single most relevant visible object under the mouse cursor—based on a logical priority stack—never indiscriminately.

KILL PRIORITY ORDER (HIGH → LOW):
Hostile pawns (e.g., raiders, manhunters, hostile factions)

Mechanoids (hostile or inactive)

Wild animals (especially manhunters)

Items (weapons, apparel, resources)

Buildings (turrets, doors, furniture, etc.)

Corpses

Filth, plants, debris, other clutter

Colonists & player-owned pawns (absolute last priority)

KEY FEATURES:
Only one thing killed per click

Follows strict priority, ignoring draw order if necessary

Skips colonists unless nothing else is present

Optional log message showing what was killed

Tooltip updated:
"Kills only the most relevant object under the mouse — enemies first, colonists last."

TO IMPLEMENT:
Patch or override DebugToolsGeneral.Kill click handler

Use Selector.SelectableObjectsAt() or equivalent to gather all Things at mouse location

Sort using the above logic

Call .Kill() or .Destroy() on the top-priority object

Optionally highlight or log the target for feedback

PSEUDOCODE:
csharp
Copy
Edit
Thing GetTopKillTarget(IntVec3 cell)
{
    var things = Find.Selector.SelectableObjectsAt(cell).OfType<Thing>().ToList();

    return things
        .OrderBy(t => GetKillPriority(t))
        .FirstOrDefault();
}

int GetKillPriority(Thing t)
{
    if (t is Pawn p)
    {
        if (p.HostileTo(Faction.OfPlayer)) return 0; // Hostile pawn
        if (p.RaceProps.IsMechanoid) return 1;       // Mechanoid
        if (p.Faction == null && !p.Dead) return 2;  // Wild animal
        if (p.IsColonist || p.Faction == Faction.OfPlayer) return 7; // Colonist or tame
        return 6; // Other pawn types
    }

    if (t.def.IsCorpse) return 5;
    if (t.def.IsItem) return 3;
    if (t.def.category == ThingCategory.Building) return 4;

    return 6; // Filth, plants, etc.
}

void KillSmartUnderCursor()
{
    var cell = UI.MouseCell();
    var target = GetTopKillTarget(cell);
    if (target != null)
    {
        target.Kill(); // Or Destroy if needed
        Log.Message($"[Smart Kill] Killed {target.LabelCap}");
    }
}
VERIFY IN GAME FILES:
Is there a shared base method for killing/destroying across Thing types?

Confirm if Mechanoids are distinguishable by RaceProps.IsMechanoid

Validate whether SelectableObjectsAt() includes corpses and filth

Make sure priority ordering doesn't get overridden by selection sort elsewhere

OPTIONAL:
Add Dev Mode toggle: "Smart Kill Mode: On/Off"

Add hold-Shift modifier to revert to vanilla "Kill All" in cell

Show hover effect or icon over the selected kill target for clarity

