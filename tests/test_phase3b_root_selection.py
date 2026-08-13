"""Canonical Modern Wi-Fi/Modern Audio operation-selection fixtures."""

import inspect
import unittest

from opencore_legacy_patcher.sys_patch import root_selection
from opencore_legacy_patcher.sys_patch.root_selection import (
    RootPatchSelection,
    SelectableRootPatch,
)


APPLICABLE = ("Networking: Modern Wireless", "Miscellaneous: Modern Audio")
PATCHES = {
    "Modern Wireless": {"wireless": True},
    "Modern Wireless Extended": {"wireless-extended": True},
    "Modern Audio": {"audio": True},
}


class RootPatchSelectionTests(unittest.TestCase):
    def test_clean_defaults_every_applicable_family_on(self) -> None:
        selection = RootPatchSelection.initialize(APPLICABLE)
        self.assertEqual(
            selection.selected,
            frozenset({SelectableRootPatch.MODERN_WIFI, SelectableRootPatch.MODERN_AUDIO}),
        )
        self.assertEqual(selection.filter_patch_dictionary(PATCHES), PATCHES)

    def test_installed_wifi_only_initializes_wifi_on_audio_off(self) -> None:
        selection = RootPatchSelection.initialize(APPLICABLE, ("Modern Wireless",))
        self.assertTrue(selection.is_selected(SelectableRootPatch.MODERN_WIFI))
        self.assertFalse(selection.is_selected(SelectableRootPatch.MODERN_AUDIO))

    def test_installed_audio_only_initializes_wifi_off_audio_on(self) -> None:
        selection = RootPatchSelection.initialize(APPLICABLE, ("Modern Audio",))
        self.assertFalse(selection.is_selected(SelectableRootPatch.MODERN_WIFI))
        self.assertTrue(selection.is_selected(SelectableRootPatch.MODERN_AUDIO))

    def test_installed_both_initializes_both_on(self) -> None:
        selection = RootPatchSelection.initialize(APPLICABLE, ("Modern Wireless", "Modern Audio"))
        self.assertEqual(selection.filter_patch_dictionary(PATCHES), PATCHES)

    def test_wifi_only_filters_every_modern_wireless_member_as_one_family(self) -> None:
        selection = RootPatchSelection.initialize(APPLICABLE).with_selection(
            SelectableRootPatch.MODERN_AUDIO,
            False,
        )
        self.assertEqual(
            set(selection.filter_patch_dictionary(PATCHES)),
            {"Modern Wireless", "Modern Wireless Extended"},
        )

    def test_audio_only_filters_modern_wireless(self) -> None:
        selection = RootPatchSelection.initialize(APPLICABLE).with_selection(
            SelectableRootPatch.MODERN_WIFI,
            False,
        )
        self.assertEqual(set(selection.filter_patch_dictionary(PATCHES)), {"Modern Audio"})

    def test_both_off_is_empty(self) -> None:
        selection = RootPatchSelection.initialize(APPLICABLE)
        selection = selection.with_selection(SelectableRootPatch.MODERN_WIFI, False)
        selection = selection.with_selection(SelectableRootPatch.MODERN_AUDIO, False)
        self.assertEqual(selection.filter_patch_dictionary(PATCHES), {})

    def test_inapplicable_family_cannot_be_selected(self) -> None:
        selection = RootPatchSelection.initialize(("Networking: Modern Wireless",))
        self.assertEqual(
            selection.with_selection(SelectableRootPatch.MODERN_AUDIO, True),
            selection,
        )

    def test_nonselectable_patch_families_are_preserved(self) -> None:
        selection = RootPatchSelection.initialize(APPLICABLE)
        selection = selection.with_selection(SelectableRootPatch.MODERN_AUDIO, False)
        patches = {**PATCHES, "Future Nonselectable Patch": {"future": True}}
        self.assertIn("Future Nonselectable Patch", selection.filter_patch_dictionary(patches))

    def test_selection_layer_has_no_hardware_identity_logic(self) -> None:
        source = inspect.getsource(root_selection)
        for forbidden in ("device_probe", "Broadcom", "Intel", "vendor_id", "device_id", "8086"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
