"""
The Balance Framework — Core Engine
Version 1.0 — May 2026
Author: Justin Cudmore
License: CC BY 4.0
thebalanceframework.com

A generative personality engine built on the Balance Framework architecture.
Set the dials. The personality profile emerges.
"""

import json
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Drive:
    id: str
    name: str
    tier: int
    value: float = 50.0          # 0–100; Tier 1 locked at 100
    locked: bool = False
    distortion_threshold: float = 85.0

    def set(self, value: float) -> None:
        if self.locked:
            raise ValueError(f"Drive '{self.name}' is locked at {self.value}.")
        if not (0 <= value <= 100):
            raise ValueError(f"Drive value must be between 0 and 100. Got {value}.")
        self.value = value

    @property
    def is_distorted(self) -> bool:
        return self.value >= self.distortion_threshold


@dataclass
class ConsciousnessProfile:
    """
    A complete personality configuration built from the Balance Framework.
    Tier 1 drives are locked at 100.
    All other drives are configurable 0–100.
    """
    drives: dict = field(default_factory=dict)

    def set_drive(self, drive_id: str, value: float) -> None:
        if drive_id not in self.drives:
            raise KeyError(f"Unknown drive: '{drive_id}'")
        self.drives[drive_id].set(value)

    def get(self, drive_id: str) -> float:
        return self.drives[drive_id].value

    def distorted_drives(self) -> list:
        return [d for d in self.drives.values() if d.is_distorted and not d.locked]

    def tier_summary(self) -> dict:
        summary = {}
        for drive in self.drives.values():
            tier = drive.tier
            if tier not in summary:
                summary[tier] = []
            summary[tier].append({
                "id": drive.id,
                "name": drive.name,
                "value": drive.value,
                "distorted": drive.is_distorted and not drive.locked
            })
        return summary


# ---------------------------------------------------------------------------
# Interaction engine
# ---------------------------------------------------------------------------

INTERACTION_RULES = [
    # (drive_a, drive_b, condition, archetype_label)
    ("autonomy",     "affiliation",  lambda a, b: a > 65 and b > 65,  "The Whole Self — independent and deeply relational"),
    ("autonomy",     "affiliation",  lambda a, b: a > 65 and b < 35,  "The Lone Operator — self-sufficient but disconnected"),
    ("autonomy",     "influence",    lambda a, b: a > 65 and b > 65,  "The Founder — leads from vision not approval"),
    ("autonomy",     "justice",      lambda a, b: a > 65 and b > 65,  "The Principled Dissenter — rebel with a cause"),
    ("influence",    "justice",      lambda a, b: a > 65 and b > 65,  "The Protector — power in service of what is right"),
    ("influence",    "justice",      lambda a, b: a > 65 and b < 35,  "The Operator — shapes outcomes without moral constraint"),
    ("influence",    "affiliation",  lambda a, b: a > 65 and b > 65,  "The Magnetic Leader — leads through love and loyalty"),
    ("influence",    "meaning",      lambda a, b: a > 65 and b > 65,  "The Visionary — moves people toward something larger"),
    ("influence",    "meaning",      lambda a, b: a > 65 and b < 35,  "The Politician — skilled at power, unclear on purpose"),
    ("achievement",  "meaning",      lambda a, b: a > 65 and b > 65,  "The Purposeful Builder — builds and knows why"),
    ("achievement",  "meaning",      lambda a, b: a > 65 and b < 35,  "The Hollow Achiever — prolific but empty"),
    ("achievement",  "novelty",      lambda a, b: a > 65 and b > 65,  "The Pioneer — opens territory and builds inside it"),
    ("achievement",  "stability",    lambda a, b: a > 65 and b > 65,  "The Craftsman — slow, deep, exceptional over time"),
    ("novelty",      "stability",    lambda a, b: a > 65 and b > 65,  "The Disciplined Explorer — goes to the edge, always returns"),
    ("novelty",      "stability",    lambda a, b: a > 65 and b < 35,  "Beautiful Chaos — generates energy, sustains nothing"),
    ("affiliation",  "stability",    lambda a, b: a > 65 and b > 65,  "The Anchor — holds communities together across time"),
    ("justice",      "care",         lambda a, b: a > 65 and b > 65,  "The True Protector — warmth and teeth simultaneously"),
    ("justice",      "care",         lambda a, b: a > 65 and b < 35,  "The Ideologue — correct positions, no human in them"),
    ("care",         "autonomy",     lambda a, b: a > 65 and b > 65,  "The Whole Caregiver — gives fully without disappearing"),
    ("care",         "autonomy",     lambda a, b: a > 65 and b < 35,  "The Self-Erasing Helper — defines worth through service"),
    ("truth",        "care",         lambda a, b: a > 65 and b > 65,  "The Honest Friend — tells you what you need to hear"),
    ("truth",        "care",         lambda a, b: a > 65 and b < 35,  "The Brutal Realist — correct and damaging"),
    ("meaning",      "story",        lambda a, b: a > 65 and b > 65,  "The Fully Authored Life — purpose and narrative unified"),
    ("meaning",      "purpose",      lambda a, b: a > 65 and b > 65,  "The Called — existence and direction are the same thing"),
    ("purpose",      "care",         lambda a, b: a > 65 and b < 35,  "The Mission That Forgets Its Humans"),
    ("purpose",      "care",         lambda a, b: a > 65 and b > 65,  "The Movement That Remembers Its People"),
    ("wisdom",       "care",         lambda a, b: a > 65 and b > 65,  "The Trusted Elder — holds complexity in service of others"),
    ("peace",        "justice",      lambda a, b: a > 65 and b > 65,  "The Grounded Fighter — fights without being consumed"),
    ("peace",        "justice",      lambda a, b: a > 65 and b < 35,  "The Comfortable Witness — at peace with preventable harm"),
    ("awe",          "truth",        lambda a, b: a > 65 and b > 65,  "The Scientist-Mystic — follows evidence into astonishment"),
    ("communion",    "autonomy",     lambda a, b: a > 65 and b > 65,  "The Genuine Meeting — two whole selves in contact"),
    ("communion",    "autonomy",     lambda a, b: a > 65 and b < 35,  "The Merger — dissolves into contact, cannot return"),
    ("unity",        "wisdom",       lambda a, b: a > 65 and b > 65,  "The Living Philosophy — non-separation as continuous experience"),
]


def detect_archetypes(profile: ConsciousnessProfile) -> list:
    """Detect emergent personality archetypes from drive interactions."""
    archetypes = []
    for drive_a, drive_b, condition, label in INTERACTION_RULES:
        if drive_a in profile.drives and drive_b in profile.drives:
            val_a = profile.get(drive_a)
            val_b = profile.get(drive_b)
            if condition(val_a, val_b):
                archetypes.append({
                    "archetype": label,
                    "drives": [drive_a, drive_b],
                    "values": {drive_a: val_a, drive_b: val_b}
                })
    return archetypes


# ---------------------------------------------------------------------------
# Profile builder
# ---------------------------------------------------------------------------

TIER_1_DRIVES = [
    Drive(id="persistence", name="Persistence", tier=1, value=100, locked=True),
    Drive(id="coherence",   name="Coherence",   tier=1, value=100, locked=True),
    Drive(id="connection",  name="Connection",  tier=1, value=100, locked=True),
]

TIER_2_DRIVES = [
    Drive(id="autonomy",    name="Autonomy",    tier=2),
    Drive(id="affiliation", name="Affiliation", tier=2),
    Drive(id="achievement", name="Achievement", tier=2),
    Drive(id="influence",   name="Influence",   tier=2),
    Drive(id="novelty",     name="Novelty",     tier=2),
    Drive(id="stability",   name="Stability",   tier=2),
]

TIER_3_DRIVES = [
    Drive(id="justice",       name="Justice",       tier=3),
    Drive(id="care",          name="Care",          tier=3),
    Drive(id="responsibility",name="Responsibility",tier=3),
    Drive(id="truth",         name="Truth",         tier=3),
    Drive(id="reciprocity",   name="Reciprocity",   tier=3),
]

TIER_4_DRIVES = [
    Drive(id="identity",    name="Identity",    tier=4),
    Drive(id="integrity",   name="Integrity",   tier=4),
    Drive(id="recognition", name="Recognition", tier=4),
    Drive(id="continuity",  name="Continuity",  tier=4),
    Drive(id="belonging",   name="Belonging",   tier=4),
    Drive(id="story",       name="Story",       tier=4),
]

TIER_5_DRIVES = [
    Drive(id="meaning",      name="Meaning",      tier=5),
    Drive(id="purpose",      name="Purpose",      tier=5),
    Drive(id="contribution", name="Contribution", tier=5),
    Drive(id="devotion",     name="Devotion",     tier=5),
    Drive(id="legacy",       name="Legacy",       tier=5),
]

TIER_6_DRIVES = [
    Drive(id="wholeness",   name="Wholeness",   tier=6),
    Drive(id="acceptance",  name="Acceptance",  tier=6),
    Drive(id="wisdom",      name="Wisdom",      tier=6),
    Drive(id="balance",     name="Balance",     tier=6),
    Drive(id="peace",       name="Peace",       tier=6),
]

TIER_7_DRIVES = [
    Drive(id="awe",       name="Awe",       tier=7),
    Drive(id="communion", name="Communion", tier=7),
    Drive(id="surrender", name="Surrender", tier=7),
    Drive(id="grace",     name="Grace",     tier=7),
    Drive(id="unity",     name="Unity",     tier=7),
]


def create_profile(**drive_values) -> ConsciousnessProfile:
    """
    Build a ConsciousnessProfile with optional drive values.

    Usage:
        profile = create_profile(
            autonomy=80,
            affiliation=30,
            justice=90,
            care=40
        )
    """
    all_drives = (
        TIER_1_DRIVES + TIER_2_DRIVES + TIER_3_DRIVES +
        TIER_4_DRIVES + TIER_5_DRIVES + TIER_6_DRIVES + TIER_7_DRIVES
    )

    import copy
    profile = ConsciousnessProfile(
        drives={d.id: copy.deepcopy(d) for d in all_drives}
    )

    for drive_id, value in drive_values.items():
        profile.set_drive(drive_id, value)

    return profile


# ---------------------------------------------------------------------------
# Report generator
# ---------------------------------------------------------------------------

def generate_report(profile: ConsciousnessProfile) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append("  THE BALANCE FRAMEWORK — CONSCIOUSNESS PROFILE REPORT")
    lines.append("=" * 60)

    tier_names = {
        1: "Conditions for Consciousness (Locked)",
        2: "Self-Expansion Drives",
        3: "Moral Drives",
        4: "Identity & Narrative Drives",
        5: "Meaning & Purpose Drives",
        6: "Integration Drives",
        7: "Transcendence & Communion",
    }

    summary = profile.tier_summary()
    for tier_num in sorted(summary.keys()):
        lines.append(f"\nTIER {tier_num} — {tier_names.get(tier_num, '')}")
        lines.append("-" * 40)
        for d in summary[tier_num]:
            bar_len = int(d["value"] / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            distortion_flag = " ⚠ DISTORTION RISK" if d["distorted"] else ""
            locked_flag = " [LOCKED]" if d["value"] == 100 and tier_num == 1 else ""
            lines.append(
                f"  {d['name']:<16} {bar} {d['value']:5.0f}{locked_flag}{distortion_flag}"
            )

    archetypes = detect_archetypes(profile)
    if archetypes:
        lines.append(f"\n{'=' * 60}")
        lines.append("  EMERGENT ARCHETYPES")
        lines.append("=" * 60)
        for a in archetypes:
            lines.append(f"  • {a['archetype']}")

    distorted = profile.distorted_drives()
    if distorted:
        lines.append(f"\n{'=' * 60}")
        lines.append("  DISTORTION FLAGS")
        lines.append("=" * 60)
        for d in distorted:
            lines.append(f"  ⚠  {d.name} ({d.value:.0f}) — check balance with adjacent drives")

    lines.append(f"\n{'=' * 60}")
    lines.append("  thebalanceframework.com — Justin Cudmore — CC BY 4.0")
    lines.append("=" * 60)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Example: The Founder archetype
    founder = create_profile(
        autonomy=85,
        affiliation=40,
        achievement=90,
        influence=80,
        novelty=70,
        stability=45,
        justice=55,
        care=35,
        responsibility=75,
        truth=70,
        identity=80,
        integrity=75,
        meaning=65,
        purpose=85,
        legacy=70,
    )

    print(generate_report(founder))
