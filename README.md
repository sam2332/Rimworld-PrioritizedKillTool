# Prioritized Kill Dev Tool

A RimWorld 1.6 mod that replaces the vanilla "Kill" debug tool with an intelligent version that prioritizes targets based on threat level.

## What It Does

Instead of killing everything under your mouse cursor indiscriminately, this mod makes the debug kill tool smart:

- **Only kills one target per click** - the most relevant one
- **Follows a logical priority system** - enemies first, colonists last  
- **Shows what was killed and why** - helpful debug logging
- **Maintains debug tool permissions** - works exactly like the original for what it targets

## Priority Order (Highest → Lowest)

1. 🎯 **Hostile pawns** - Raiders, manhunters, hostile faction members
2. 🤖 **Mechanoids** - Both hostile and inactive mechanoids
3. 🐺 **Wild animals** - Including manhunters and regular wildlife
4. 📦 **Items** - Weapons, apparel, resources, dropped items
5. 🏗️ **Buildings** - Turrets, doors, furniture, structures
6. 💀 **Corpses** - Dead bodies and remains
7. 🌿 **Other** - Filth, plants, debris, neutral pawns
8. 👥 **Colonists & Tamed** - Player pawns and tamed animals (absolute last resort)

## How to Use

1. Enable Developer Mode (`F12` or Options menu)
2. Open Debug Actions (`Ctrl+F12`)
3. Use the "Kill" tool as normal - it now intelligently prioritizes targets!

The tool tooltip remains "Kill" but the behavior is completely replaced.

## Installation

1. Download/clone this mod to your RimWorld Mods folder
2. Enable it in the mod list
3. No restart required - works immediately

## Technical Details

- **Harmony patch** replaces `DebugToolsGeneral.Kill()` method
- **Uses `Selector.SelectableObjectsAt()`** to find all targets at mouse position
- **Sorts by priority** and kills only the highest priority target
- **Maintains original debug permissions** through reflection

## Compatibility

- **RimWorld 1.6** - Built and tested for current version
- **Mod compatibility** - Should work with any other mods
- **No performance impact** - Only runs when using the debug kill tool

## Development

This mod was created by ProgrammerLily based on the specifications in `Mod_Base.md`. The implementation prioritizes safety (colonists last) while maintaining the power of the original debug tool for development purposes.

For technical details, see `IMPLEMENTATION_SUMMARY.md`.
