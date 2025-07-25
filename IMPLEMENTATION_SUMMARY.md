# Prioritized Kill Tool - Implementation Summary

## Overview
This mod replaces the vanilla "Kill" debug tool with an intelligent version that prioritizes targets according to a logical hierarchy.

## How It Works

### Harmony Patch
- **Target Method**: `DebugToolsGeneral.Kill()`
- **Patch Type**: Prefix patch that completely replaces the original functionality
- **Result**: The original kill-everything behavior is replaced with our smart targeting

### Priority System
The mod uses `Selector.SelectableObjectsAt()` to get all valid targets at the mouse position, then sorts them by priority:

1. **Hostile Pawns** (Priority 0) - Raiders, manhunters, hostile faction members
2. **Mechanoids** (Priority 1) - Both hostile and inactive mechanoids  
3. **Wild Animals** (Priority 2) - Including manhunters and regular wild animals
4. **Items** (Priority 3) - Weapons, apparel, resources, etc.
5. **Buildings** (Priority 4) - Turrets, doors, furniture, structures
6. **Corpses** (Priority 5) - Dead bodies and corpse things
7. **Other/Filth** (Priority 6) - Plants, debris, neutral pawns
8. **Colonists/Tamed** (Priority 7) - Player pawns and tamed animals (lowest priority)

## Key Features
- **Single Target**: Only kills one object per click (default mode)
- **Radius Mode**: Optional area-of-effect killing within configurable radius
- **Smart Selection**: Prioritizes threats over friendlies
- **Comprehensive Settings**: Full customization through mod options
- **Target Type Toggles**: Enable/disable each priority category
- **Debug Logging**: Shows what was killed and why (toggleable)
- **Safety**: Colonists are only targeted if enabled and nothing else is available
- **Distance Prioritization**: Optional preference for closer targets
- **Compatibility**: Uses reflection to maintain original debug tool permissions

## Technical Implementation

### Core Methods
- `SmartKillUnderCursor()`: Main logic entry point with settings integration
- `GetTopKillTarget()`: Finds highest priority target at mouse position (single mode)
- `GetTargetsInRadius()`: Finds all valid targets within radius (radius mode)
- `KillTargets()`: Handles killing multiple targets with proper cleanup
- `IsTargetTypeEnabled()`: Checks if target type is enabled in settings
- `GetKillPriority()`: Determines priority value for any Thing
- `GetPawnKillPriority()`: Specialized priority logic for pawns
- `GetKillPriorityName()`: Human-readable priority names for logging

### Settings System
- `PrioritizedKillToolMod`: Main mod class inheriting from Mod for settings support
- `PrioritizedKillToolSettings`: ModSettings class with ExposeData for persistence
- Comprehensive UI with checkboxes, sliders, and help text
- Real-time settings application (no restart required)

### Reflection Usage
The mod uses Harmony's `AccessTools` to temporarily enable `Thing.allowDestroyNonDestroyable` during kill operations, maintaining compatibility with the original debug tool's destructive capabilities.

## Compatibility
- **RimWorld Version**: 1.6
- **Dependencies**: Harmony (included with base game)
- **Mod Compatibility**: Should work with most other mods as it only patches the debug kill tool

## Future Enhancements
- Optional settings for priority customization
- Visual highlighting of selected target before killing
- Shift-click modifier to revert to vanilla behavior
- Custom keybind for the smart kill tool
