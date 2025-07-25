using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace PrioritizedKillTool
{
    /// <summary>
    /// Main mod class that handles loading and settings
    /// </summary>
    public class PrioritizedKillToolMod : Mod
    {
        public static PrioritizedKillToolSettings Settings;

        public PrioritizedKillToolMod(ModContentPack content) : base(content)
        {
            Settings = GetSettings<PrioritizedKillToolSettings>();
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            Settings.DoWindowContents(inRect);
        }

        public override string SettingsCategory()
        {
            return "Prioritized Kill Tool";
        }
    }

    /// <summary>
    /// Settings for the mod
    /// </summary>
    public class PrioritizedKillToolSettings : ModSettings
    {
        // Toggle for each kill type
        public bool enableHostilePawns = true;
        public bool enableMechanoids = true;
        public bool enableWildAnimals = true;
        public bool enableItems = true;
        public bool enableBuildings = true;
        public bool enableCorpses = true;
        public bool enableOther = true;
        public bool enableColonistsAndTamed = true;

        // Radius settings
        public float killRadius = 1f;
        public bool useRadiusMode = false;

        // General settings
        public bool showLogMessages = true;
        public bool prioritizeByDistance = false;

        public override void ExposeData()
        {
            Scribe_Values.Look(ref enableHostilePawns, "enableHostilePawns", true);
            Scribe_Values.Look(ref enableMechanoids, "enableMechanoids", true);
            Scribe_Values.Look(ref enableWildAnimals, "enableWildAnimals", true);
            Scribe_Values.Look(ref enableItems, "enableItems", true);
            Scribe_Values.Look(ref enableBuildings, "enableBuildings", true);
            Scribe_Values.Look(ref enableCorpses, "enableCorpses", true);
            Scribe_Values.Look(ref enableOther, "enableOther", true);
            Scribe_Values.Look(ref enableColonistsAndTamed, "enableColonistsAndTamed", true);
            
            Scribe_Values.Look(ref killRadius, "killRadius", 1f);
            Scribe_Values.Look(ref useRadiusMode, "useRadiusMode", false);
            
            Scribe_Values.Look(ref showLogMessages, "showLogMessages", true);
            Scribe_Values.Look(ref prioritizeByDistance, "prioritizeByDistance", false);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard listing = new Listing_Standard();
            listing.Begin(inRect);

            // Header
            Text.Font = GameFont.Medium;
            listing.Label("Prioritized Kill Tool Settings");
            Text.Font = GameFont.Small;
            listing.Gap();

            // Kill type toggles
            listing.Label("Target Types (Priority Order):");
            listing.Gap(6f);

            listing.CheckboxLabeled("1. Hostile Pawns (Raiders, Manhunters)", ref enableHostilePawns, 
                "Kill hostile pawns like raiders and manhunters");
            listing.CheckboxLabeled("2. Mechanoids", ref enableMechanoids, 
                "Kill mechanoids (both hostile and inactive)");
            listing.CheckboxLabeled("3. Wild Animals", ref enableWildAnimals, 
                "Kill wild animals including manhunters");
            listing.CheckboxLabeled("4. Items", ref enableItems, 
                "Kill items like weapons, apparel, and resources");
            listing.CheckboxLabeled("5. Buildings", ref enableBuildings, 
                "Kill buildings like turrets, doors, and furniture");
            listing.CheckboxLabeled("6. Corpses", ref enableCorpses, 
                "Kill corpses and dead bodies");
            listing.CheckboxLabeled("7. Other (Filth, Plants)", ref enableOther, 
                "Kill filth, plants, debris, and other objects");
            listing.CheckboxLabeled("8. Colonists & Tamed", ref enableColonistsAndTamed, 
                "Kill colonists and tamed animals (DANGER: Only enable if needed!)");

            listing.Gap();

            // Radius settings
            listing.Label("Radius Settings:");
            listing.Gap(6f);

            listing.CheckboxLabeled("Use Radius Mode", ref useRadiusMode, 
                "Scan within radius and kill all targets of the highest priority type found");
            
            if (useRadiusMode)
            {
                listing.Label($"Kill Radius: {killRadius:F1} tiles");
                killRadius = listing.Slider(killRadius, 0.5f, 10f);
                listing.Gap(6f);
                listing.Label("Note: In radius mode, the tool will scan all cells within the radius,");
                listing.Label("identify the highest priority target type present, and kill ALL targets");
                listing.Label("of that type only. Lower priority targets will be ignored.");
            }

            listing.Gap();

            // General settings
            listing.Label("General Settings:");
            listing.Gap(6f);

            listing.CheckboxLabeled("Show Log Messages", ref showLogMessages, 
                "Show messages in the log when something is killed");
            listing.CheckboxLabeled("Prioritize by Distance", ref prioritizeByDistance, 
                "When same priority, prefer closer targets");

            listing.Gap();

            // Info section
            if (listing.ButtonText("Reset to Defaults"))
            {
                ResetToDefaults();
            }

            listing.Gap();
            listing.Label("Note: Changes take effect immediately. The kill tool will respect these settings.");

            listing.End();
        }

        private void ResetToDefaults()
        {
            enableHostilePawns = true;
            enableMechanoids = true;
            enableWildAnimals = true;
            enableItems = true;
            enableBuildings = true;
            enableCorpses = true;
            enableOther = true;
            enableColonistsAndTamed = true;
            
            killRadius = 1f;
            useRadiusMode = false;
            
            showLogMessages = true;
            prioritizeByDistance = false;
        }
    }

    [StaticConstructorOnStartup]
    public static class PrioritizedKillToolStartup
    {
        static PrioritizedKillToolStartup()
        {
            var harmony = new Harmony("ProgrammerLily.PrioritizedKillTool");
            harmony.PatchAll();
            Log.Message("[Prioritized Kill Tool] Successfully patched debug kill tool");
        }
    }

    /// <summary>
    /// Harmony patch to replace the vanilla Kill debug tool with our prioritized version
    /// </summary>
    [HarmonyPatch(typeof(DebugToolsGeneral))]
    [HarmonyPatch("Kill")]
    public static class DebugToolsGeneral_Kill_Patch
    {
        [HarmonyPrefix]
        public static bool Prefix()
        {
            // TODO: Add shift key check to use vanilla behavior when shift is held
            // Currently removed due to Input class not being available in this context
            
            // Replace the vanilla kill behavior with our smart kill
            SmartKillUnderCursor();
            return false; // Skip original method
        }

        /// <summary>
        /// Our smart kill implementation that prioritizes targets
        /// </summary>
        public static void SmartKillUnderCursor()
        {
            var cell = UI.MouseCell();
            if (!cell.InBounds(Find.CurrentMap))
            {
                return;
            }

            var settings = PrioritizedKillToolMod.Settings;
            List<Thing> targets;

            if (settings.useRadiusMode)
            {
                targets = GetTargetsInRadius(cell, settings.killRadius);
                
                if (settings.showLogMessages && targets.Any())
                {
                    var priorityName = targets.First() != null ? GetKillPriorityName(targets.First()) : "Unknown";
                    Log.Message(
                        $"[Prioritized Kill Tool] Using radius mode at {cell} (radius: {settings.killRadius:F1})"
                    );
                }
            }
            else
            {
                var singleTarget = GetTopKillTarget(cell);
                targets = singleTarget != null ? new List<Thing> { singleTarget } : new List<Thing>();
                
                if (settings.showLogMessages && targets.Any())
                {
                    Log.Message(
                        $"[Prioritized Kill Tool] Using single-target mode at {cell}"
                    );
                }
            }

            if (targets.Any())
            {
                KillTargets(targets);
            }
            else if (settings.showLogMessages)
            {
                Log.Message("[Prioritized Kill Tool] No valid targets found at cursor");
            }
        }

        /// <summary>
        /// Get all valid targets within the specified radius, but only return targets of the highest priority type found
        /// </summary>
        private static List<Thing> GetTargetsInRadius(IntVec3 center, float radius)
        {
            var map = Find.CurrentMap;
            var allTargets = new List<Thing>();
            var settings = PrioritizedKillToolMod.Settings;

            // Get all cells within radius
            var cellsInRadius = GenRadial.RadialCellsAround(center, radius, true)
                .Where(c => c.InBounds(map));

            foreach (var cell in cellsInRadius)
            {
                var cellTargets = Selector.SelectableObjectsAt(cell, map)
                    .OfType<Thing>()
                    .Where(t => t != null && !t.Destroyed && IsTargetTypeEnabled(t, settings))
                    .ToList();

                allTargets.AddRange(cellTargets);
            }

            // If no targets found, return empty list
            if (!allTargets.Any())
            {
                return new List<Thing>();
            }

            // Find the highest priority (lowest number) among all targets
            int highestPriority = allTargets.Min(t => GetKillPriority(t));

            // Filter to only include targets with the highest priority
            var topPriorityTargets = allTargets
                .Where(t => GetKillPriority(t) == highestPriority)
                .ToList();

            // Sort the top priority targets, optionally by distance
            if (settings.prioritizeByDistance)
            {
                return topPriorityTargets
                    .OrderBy(t => t.Position.DistanceTo(center))
                    .ThenBy(t => t.def.defName)
                    .ToList();
            }
            else
            {
                return topPriorityTargets
                    .OrderBy(t => t.def.defName)
                    .ToList();
            }
        }

        /// <summary>
        /// Kill all targets in the list
        /// </summary>
        private static void KillTargets(List<Thing> targets)
        {
            var settings = PrioritizedKillToolMod.Settings;
            var allowDestroyField = AccessTools.Field(typeof(Thing), "allowDestroyNonDestroyable");
            bool originalValue = (bool)allowDestroyField.GetValue(null);

            try
            {
                allowDestroyField.SetValue(null, true);
                
                // Log summary for radius mode
                if (settings.useRadiusMode && targets.Count > 1 && settings.showLogMessages)
                {
                    var priorityName = targets.Any() ? GetKillPriorityName(targets.First()) : "Unknown";
                    Log.Message(
                        $"[Prioritized Kill Tool] Radius mode: Found {targets.Count} targets of type '{priorityName}' (highest priority found)"
                    );
                }
                
                foreach (var target in targets)
                {
                    if (target != null && !target.Destroyed)
                    {
                        target.Kill();
                        
                        if (settings.showLogMessages)
                        {
                            Log.Message(
                                $"[Prioritized Kill Tool] Killed {target.LabelCap} (Priority: {GetKillPriorityName(target)})"
                            );
                        }
                    }
                }
            }
            finally
            {
                allowDestroyField.SetValue(null, originalValue);
            }
        }

        /// <summary>
        /// Check if a target type is enabled in settings
        /// </summary>
        private static bool IsTargetTypeEnabled(Thing t, PrioritizedKillToolSettings settings)
        {
            if (t is Pawn p)
            {
                // Dead pawns (corpses) 
                if (p.Dead) 
                    return settings.enableCorpses;

                // Hostile pawns
                if (p.HostileTo(Faction.OfPlayer)) 
                    return settings.enableHostilePawns;

                // Mechanoids
                if (p.RaceProps.IsMechanoid) 
                    return settings.enableMechanoids;

                // Wild animals
                if (p.Faction == null && !p.Dead) 
                    return settings.enableWildAnimals;

                // Player colonists and tamed animals
                if (p.IsColonist || p.Faction == Faction.OfPlayer) 
                    return settings.enableColonistsAndTamed;

                // Other pawn types (neutral, etc.)
                return settings.enableOther;
            }

            // Non-pawn things
            if (t.def.IsCorpse) 
                return settings.enableCorpses;
            if (t.def.category == ThingCategory.Item) 
                return settings.enableItems;
            if (t.def.category == ThingCategory.Building) 
                return settings.enableBuildings;
            
            // Filth, plants, etc.
            return settings.enableOther;
        }

        /// <summary>
        /// Get the highest priority target to kill at the specified cell
        /// </summary>
        private static Thing GetTopKillTarget(IntVec3 cell)
        {
            var settings = PrioritizedKillToolMod.Settings;
            
            // Use SelectableObjectsAt to get all things at the location
            var things = Selector
                .SelectableObjectsAt(cell, Find.CurrentMap)
                .OfType<Thing>()
                .Where(t => t != null && !t.Destroyed && IsTargetTypeEnabled(t, settings))
                .ToList();

            if (!things.Any())
            {
                return null;
            }

            // Sort by priority, then optionally by distance
            if (settings.prioritizeByDistance)
            {
                return things
                    .OrderBy(t => GetKillPriority(t))
                    .ThenBy(t => t.Position.DistanceTo(cell))
                    .ThenBy(t => t.def.defName)
                    .FirstOrDefault();
            }
            else
            {
                return things
                    .OrderBy(t => GetKillPriority(t))
                    .ThenBy(t => t.def.defName) // Secondary sort for consistency
                    .FirstOrDefault();
            }
        }

        /// <summary>
        /// Get the kill priority for a thing (lower number = higher priority)
        /// </summary>
        private static int GetKillPriority(Thing t)
        {
            if (t is Pawn p)
            {
                return GetPawnKillPriority(p);
            }

            // Non-pawn things
            if (t.def.IsCorpse)
                return 5;
            if (t.def.category == ThingCategory.Item)
                return 3;
            if (t.def.category == ThingCategory.Building)
                return 4;

            // Filth, plants, etc.
            return 6;
        }

        /// <summary>
        /// Get kill priority specifically for pawns
        /// </summary>
        private static int GetPawnKillPriority(Pawn p)
        {
            // Dead pawns (corpses) should be handled by the corpse category above,
            // but just in case, treat dead pawns as low priority
            if (p.Dead)
                return 5;

            // Hostile pawns get highest priority
            if (p.HostileTo(Faction.OfPlayer))
                return 0;

            // Mechanoids (includes both hostile and inactive)
            if (p.RaceProps.IsMechanoid)
                return 1;

            // Wild animals, especially manhunters
            if (p.Faction == null && !p.Dead)
            {
                // Manhunters get slightly higher priority than regular wild animals
                if (p.InMentalState && p.MentalStateDef?.category == MentalStateCategory.Aggro)
                {
                    return 2;
                }
                return 2; // All wild animals
            }

            // Player colonists and tamed animals get lowest priority
            if (p.IsColonist || p.Faction == Faction.OfPlayer)
                return 7;

            // Other pawn types (neutral, etc.)
            return 6;
        }

        /// <summary>
        /// Get a human-readable name for the kill priority (for logging)
        /// </summary>
        private static string GetKillPriorityName(Thing t)
        {
            int priority = GetKillPriority(t);

            if (t is Pawn p)
            {
                switch (priority)
                {
                    case 0:
                        return "Hostile Pawn";
                    case 1:
                        return "Mechanoid";
                    case 2:
                        return
                            p.InMentalState
                            && p.MentalStateDef?.category == MentalStateCategory.Aggro
                            ? "Manhunter"
                            : "Wild Animal";
                    case 5:
                        return "Dead Pawn";
                    case 6:
                        return "Neutral Pawn";
                    case 7:
                        return "Colonist/Tamed";
                    default:
                        return "Unknown Pawn";
                }
            }
            else
            {
                switch (priority)
                {
                    case 3:
                        return "Item";
                    case 4:
                        return "Building";
                    case 5:
                        return "Corpse";
                    case 6:
                        return "Other";
                    default:
                        return "Unknown Thing";
                }
            }
        }
    }
}
