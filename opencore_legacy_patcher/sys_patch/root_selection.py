"""Canonical user selection for applicable KGP root patch families."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


EMPTY_SELECTION_MESSAGE = "Please select at least one patching option."


class SelectableRootPatch(StrEnum):
    MODERN_WIFI = "modern-wifi"
    MODERN_AUDIO = "modern-audio"


@dataclass(frozen=True)
class SelectableRootPatchDefinition:
    identifier: SelectableRootPatch
    display_name: str
    description: str
    hardware_patchset_name: str
    patch_names: frozenset[str]


SELECTABLE_ROOT_PATCHES = (
    SelectableRootPatchDefinition(
        identifier=SelectableRootPatch.MODERN_WIFI,
        display_name="Modern Wi-Fi",
        description="Modern wireless root patches",
        hardware_patchset_name="Networking: Modern Wireless",
        patch_names=frozenset({"Modern Wireless", "Modern Wireless Extended"}),
    ),
    SelectableRootPatchDefinition(
        identifier=SelectableRootPatch.MODERN_AUDIO,
        display_name="Modern Audio",
        description="AppleHDA root patches",
        hardware_patchset_name="Miscellaneous: Modern Audio",
        patch_names=frozenset({"Modern Audio"}),
    ),
)

_DEFINITIONS_BY_ID = {definition.identifier: definition for definition in SELECTABLE_ROOT_PATCHES}
_DEFINITIONS_BY_HARDWARE_NAME = {
    definition.hardware_patchset_name: definition for definition in SELECTABLE_ROOT_PATCHES
}
_DEFINITIONS_BY_PATCH_NAME = {
    patch_name: definition
    for definition in SELECTABLE_ROOT_PATCHES
    for patch_name in definition.patch_names
}


@dataclass(frozen=True)
class RootPatchSelection:
    """One immutable current operation selection, constrained by applicability."""

    applicable: frozenset[SelectableRootPatch]
    selected: frozenset[SelectableRootPatch]

    def __post_init__(self) -> None:
        if not self.selected.issubset(self.applicable):
            raise ValueError("Selected root patches must be applicable")

    @classmethod
    def initialize(
        cls,
        applicable_hardware_patchsets: tuple[str, ...] | list[str] | set[str],
        installed_patch_names: tuple[str, ...] | list[str] | None = None,
    ) -> RootPatchSelection:
        applicable = frozenset(
            _DEFINITIONS_BY_HARDWARE_NAME[name].identifier
            for name in applicable_hardware_patchsets
            if name in _DEFINITIONS_BY_HARDWARE_NAME
        )
        if installed_patch_names is None:
            return cls(applicable=applicable, selected=applicable)

        installed_families = {
            _DEFINITIONS_BY_PATCH_NAME[name].identifier
            for name in installed_patch_names
            if name in _DEFINITIONS_BY_PATCH_NAME
        }
        return cls(applicable=applicable, selected=frozenset(installed_families) & applicable)

    def with_selection(self, identifier: SelectableRootPatch, selected: bool) -> RootPatchSelection:
        if identifier not in self.applicable:
            return self
        updated = set(self.selected)
        if selected:
            updated.add(identifier)
        else:
            updated.discard(identifier)
        return RootPatchSelection(self.applicable, frozenset(updated))

    def constrained_to(self, applicable_hardware_patchsets: tuple[str, ...] | list[str] | set[str]) -> RootPatchSelection:
        applicable = frozenset(
            _DEFINITIONS_BY_HARDWARE_NAME[name].identifier
            for name in applicable_hardware_patchsets
            if name in _DEFINITIONS_BY_HARDWARE_NAME
        )
        return RootPatchSelection(applicable=applicable, selected=self.selected & applicable)

    def is_applicable(self, identifier: SelectableRootPatch) -> bool:
        return identifier in self.applicable

    def is_selected(self, identifier: SelectableRootPatch) -> bool:
        return identifier in self.selected

    def is_empty(self) -> bool:
        return not self.selected

    def is_hardware_patchset_selected(self, hardware_patchset_name: str) -> bool:
        definition = _DEFINITIONS_BY_HARDWARE_NAME.get(hardware_patchset_name)
        if definition is None:
            return True
        return definition.identifier in self.selected

    def filter_patch_dictionary(self, patches: dict) -> dict:
        """Exclude deselected selectable families; preserve every nonselectable patch."""
        return {
            name: patch
            for name, patch in patches.items()
            if (
                name not in _DEFINITIONS_BY_PATCH_NAME
                or _DEFINITIONS_BY_PATCH_NAME[name].identifier in self.selected
            )
        }

    def display_names(self) -> tuple[str, ...]:
        return tuple(
            definition.display_name
            for definition in SELECTABLE_ROOT_PATCHES
            if definition.identifier in self.selected
        )


def definition_for(identifier: SelectableRootPatch) -> SelectableRootPatchDefinition:
    return _DEFINITIONS_BY_ID[identifier]
