"""
gui_sys_patch_display.py: Display root patching menu
"""

import wx
import logging
import threading

from .. import constants

from ..sys_patch.patchsets import HardwarePatchsetDetection, HardwarePatchsetValidation
from ..sys_patch.root_selection import (
    SELECTABLE_ROOT_PATCHES,
    RootPatchSelection,
    SelectableRootPatch,
)
from ..sys_patch.root_state import RootPatchStateEvaluator, RootPatchState

from ..wx_gui import (
    gui_main_menu,
    gui_support,
    gui_sys_patch_start,
)


class SysPatchDisplayFrame(wx.Frame):
    """
    Create a modal frame for displaying root patches
    """
    def __init__(self, parent: wx.Frame, title: str, global_constants: constants.Constants, screen_location: tuple = None):
        logging.info("Initializing Root Patch Display Frame")

        if parent:
            self.frame = parent
        else:
            super().__init__(parent, title=title, size=(360, 200), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
            self.frame = self
            self.frame.Centre()

        self.title = title
        self.constants: constants.Constants = global_constants
        self.frame_modal: wx.Dialog = None
        self.return_button: wx.Button = None
        self.available_patches: bool = False
        self.init_with_parent = True if parent else False
        self.selection: RootPatchSelection = RootPatchSelection(frozenset(), frozenset())
        self.selection_checkboxes: dict[SelectableRootPatch, wx.CheckBox] = {}
        self.selection_summary: wx.StaticText = None
        self.selection_state_label: wx.StaticText = None
        self.start_button: wx.Button = None
        self.revert_button: wx.Button = None
        self.current_detection: HardwarePatchsetDetection = None
        self.requested_patchset: dict = {}
        self.root_state = None

        self.frame_modal = wx.Dialog(self.frame, title=title, size=(360, 200))

        self._generate_elements_display_patches(self.frame_modal)

        if self.constants.update_stage != gui_support.AutoUpdateStages.INACTIVE:
            if self.available_patches is False:
                gui_support.RestartHost(self.frame).restart(message="No root patch updates needed!\n\nWould you like to reboot to apply the new OpenCore build?")


    def _generate_elements_display_patches(self, frame: wx.Frame = None) -> None:
        """
        Generate UI elements for root patching frame

        Format:
            - Title label:        Post-Install Menu
            - Label:              Available patches:
            - Labels:             {patch name}
            - Button:             Start Root Patching
            - Button:             Revert Root Patches
            - Button:             Return to Main Menu
        """
        frame = self if not frame else frame

        title_label = wx.StaticText(frame, label="Post-Install Menu", pos=(-1, 10))
        title_label.SetFont(gui_support.font_factory(19, wx.FONTWEIGHT_BOLD))
        title_label.Centre(wx.HORIZONTAL)

        # Label: Fetching patches...
        available_label = wx.StaticText(frame, label="Fetching patches for host", pos=(-1, title_label.GetPosition()[1] + title_label.GetSize()[1] + 10))
        available_label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_BOLD))
        available_label.Centre(wx.HORIZONTAL)

        # Progress bar
        progress_bar = wx.Gauge(frame, range=100, pos=(-1, available_label.GetPosition()[1] + available_label.GetSize()[1] + 10), size=(250, 20))
        progress_bar.Centre(wx.HORIZONTAL)
        progress_bar_animation = gui_support.GaugePulseCallback(self.constants, progress_bar)
        progress_bar_animation.start_pulse()

        # Set window height
        frame.SetSize((-1, progress_bar.GetPosition()[1] + progress_bar.GetSize()[1] + 40))

        # Labels: {patch name}
        patches: dict = {}
        requested_patchset: dict = {}
        detection: HardwarePatchsetDetection = None
        def _fetch_patches(self) -> None:
            nonlocal patches, requested_patchset, detection
            detection = HardwarePatchsetDetection(constants=self.constants)
            patches = detection.device_properties
            requested_patchset = detection.patches

        thread = threading.Thread(target=_fetch_patches, args=(self,))
        thread.start()

        frame.ShowWindowModal()

        gui_support.wait_for_thread(thread)

        frame.Close()

        progress_bar.Hide()
        progress_bar_animation.stop_pulse()

        available_label.SetLabel("Available patches for your system:")
        available_label.Centre(wx.HORIZONTAL)


        if not any(not patch.startswith("Settings") and not patch.startswith("Validation") and patches[patch] is True for patch in patches):
            logging.info("No applicable patches available")
            patches = {}

        applicable_patchsets = tuple(
            patch
            for patch, enabled in patches.items()
            if not patch.startswith("Settings") and not patch.startswith("Validation") and enabled is True
        )
        bootstrap_state = RootPatchStateEvaluator(self.constants).evaluate(requested_patchset)
        self.selection = RootPatchSelection.initialize(
            applicable_patchsets,
            bootstrap_state.installed_selection,
        )
        requested_patchset = self.selection.filter_patch_dictionary(requested_patchset)
        root_state = RootPatchStateEvaluator(self.constants).evaluate(requested_patchset)

        if not patches:
            # Prompt user with no patches found
            patch_label = wx.StaticText(frame, label="No patches required", pos=(-1, available_label.GetPosition()[1] + 20))
            patch_label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
            patch_label.Centre(wx.HORIZONTAL)

        else:
            # Add Label for each patch
            i = 0
            longest_patch = ""
            for patch in patches:
                if (not patch.startswith("Settings") and not patch.startswith("Validation") and patches[patch] is True):
                    if len(patch) > len(longest_patch):
                        longest_patch = patch
            anchor = wx.StaticText(frame, label=longest_patch, pos=(-1, available_label.GetPosition()[1] + 20))
            anchor.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
            anchor.Centre(wx.HORIZONTAL)
            anchor.Hide()

            logging.info("Available patches:")
            for patch in patches:
                if (not patch.startswith("Settings") and not patch.startswith("Validation") and patches[patch] is True):
                    i = i + 20
                    logging.info(f"- {patch}")
                    patch_label = wx.StaticText(frame, label=f"- {patch}", pos=(anchor.GetPosition()[0], available_label.GetPosition()[1] + i))
                    patch_label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))

            if i == 20:
                patch_label.SetLabel(patch_label.GetLabel().replace("-", ""))
                patch_label.Centre(wx.HORIZONTAL)

            if patches[HardwarePatchsetValidation.PATCHING_NOT_POSSIBLE] is True:
                # Cannot patch due to the following reasons:
                patch_label = wx.StaticText(frame, label="Cannot patch due to the following reasons:", pos=(-1, patch_label.GetPosition()[1] + 25))
                patch_label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_BOLD))
                patch_label.Centre(wx.HORIZONTAL)

                longest_patch = ""
                for patch in patches:
                    if not patch.startswith("Validation"):
                        continue
                    if patches[patch] is False:
                        continue
                    if patch in [HardwarePatchsetValidation.PATCHING_NOT_POSSIBLE, HardwarePatchsetValidation.UNPATCHING_NOT_POSSIBLE]:
                        continue

                    if len(patch) > len(longest_patch):
                        longest_patch = patch
                anchor = wx.StaticText(frame, label=longest_patch.split('Validation: ')[1], pos=(-1, patch_label.GetPosition()[1] + 20))
                anchor.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
                anchor.Centre(wx.HORIZONTAL)
                anchor.Hide()

                i = 0
                for patch in patches:
                    if not patch.startswith("Validation"):
                        continue
                    if patches[patch] is False:
                        continue
                    if patch in [HardwarePatchsetValidation.PATCHING_NOT_POSSIBLE, HardwarePatchsetValidation.UNPATCHING_NOT_POSSIBLE]:
                        continue

                    patch_label = wx.StaticText(frame, label=f"- {patch.split('Validation: ')[1]}", pos=(anchor.GetPosition()[0], anchor.GetPosition()[1] + i))
                    patch_label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
                    i = i + 20

                if i == 20:
                    patch_label.SetLabel(patch_label.GetLabel().replace("-", ""))
                    patch_label.Centre(wx.HORIZONTAL)

            else:
                if self.constants.computer.oclp_sys_version and self.constants.computer.oclp_sys_date:
                    date = self.constants.computer.oclp_sys_date.split(" @")
                    date = date[0] if len(date) == 2 else ""

                    patch_text = f"{self.constants.computer.oclp_sys_version}, {date}"

                    patch_label = wx.StaticText(frame, label="Root Volume last patched:", pos=(-1, patch_label.GetPosition().y + 25))
                    patch_label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_BOLD))
                    patch_label.Centre(wx.HORIZONTAL)

                    patch_label = wx.StaticText(frame, label=patch_text, pos=(available_label.GetPosition().x - 10, patch_label.GetPosition().y + 20))
                    patch_label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
                    patch_label.Centre(wx.HORIZONTAL)


        selection_title = wx.StaticText(frame, label="Root Patch Selection", pos=(-1, patch_label.GetPosition().y + 25))
        selection_title.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_BOLD))
        selection_title.Centre(wx.HORIZONTAL)

        selection_y = selection_title.GetPosition().y + 23
        for definition in SELECTABLE_ROOT_PATCHES:
            if self.selection.is_applicable(definition.identifier) is False:
                continue
            checkbox = wx.CheckBox(frame, label=definition.display_name, pos=(55, selection_y))
            checkbox.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
            checkbox.SetToolTip(definition.description)
            checkbox.SetValue(self.selection.is_selected(definition.identifier))
            checkbox.Bind(
                wx.EVT_CHECKBOX,
                lambda event, identifier=definition.identifier: self.on_patch_selection_changed(
                    identifier,
                    event.IsChecked(),
                ),
            )
            self.selection_checkboxes[definition.identifier] = checkbox
            selection_y += 23

        self.selection_summary = wx.StaticText(frame, label="", pos=(-1, selection_y + 2))
        self.selection_summary.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_BOLD))
        self.selection_summary.Centre(wx.HORIZONTAL)

        self.selection_state_label = wx.StaticText(frame, label="", pos=(-1, self.selection_summary.GetPosition().y + 22))
        self.selection_state_label.SetFont(gui_support.font_factory(12, wx.FONTWEIGHT_NORMAL))
        self.selection_state_label.Wrap(330)
        self.selection_state_label.Centre(wx.HORIZONTAL)

        # Button: Start Root Patching
        start_button = wx.Button(frame, label="Start Root Patching", pos=(10, self.selection_state_label.GetPosition().y + 38), size=(170, 30))
        start_button.Bind(wx.EVT_BUTTON, self.on_start_root_patching)
        start_button.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
        start_button.Centre(wx.HORIZONTAL)
        self.start_button = start_button

        # Button: Revert Root Patches
        revert_button = wx.Button(frame, label="Revert Root Patches", pos=(10, start_button.GetPosition().y + start_button.GetSize().height - 5), size=(170, 30))
        revert_button.Bind(wx.EVT_BUTTON, self.on_revert_root_patching)
        revert_button.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
        revert_button.Centre(wx.HORIZONTAL)
        self.revert_button = revert_button

        # Button: Return to Main Menu
        return_button = wx.Button(frame, label="Return to Main Menu", pos=(10, revert_button.GetPosition().y + revert_button.GetSize().height), size=(150, 30))
        return_button.Bind(wx.EVT_BUTTON, self.on_return_dismiss if self.init_with_parent else self.on_return_to_main_menu)
        return_button.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
        return_button.Centre(wx.HORIZONTAL)
        self.return_button = return_button

        self.current_detection = detection
        self.requested_patchset = requested_patchset
        self.root_state = root_state
        self._refresh_selection_state()

        # Set frame size
        frame.SetSize((-1, return_button.GetPosition().y + return_button.GetSize().height + 15))
        frame.ShowWindowModal()


    def _applicable_patchsets(self, detection: HardwarePatchsetDetection) -> tuple[str, ...]:
        return tuple(
            patch
            for patch, enabled in detection.device_properties.items()
            if not patch.startswith("Settings") and not patch.startswith("Validation") and enabled is True
        )


    def _refresh_selection_state(self) -> None:
        detection = HardwarePatchsetDetection(constants=self.constants)
        self.selection = self.selection.constrained_to(self._applicable_patchsets(detection))
        requested_patchset = self.selection.filter_patch_dictionary(detection.patches)
        root_state = RootPatchStateEvaluator(self.constants).evaluate(requested_patchset)

        self.current_detection = detection
        self.requested_patchset = requested_patchset
        self.root_state = root_state

        for identifier, checkbox in self.selection_checkboxes.items():
            checkbox.SetValue(self.selection.is_selected(identifier))

        selected_names = self.selection.display_names()
        selected_label = " + ".join(selected_names) if selected_names else "None"
        self.selection_summary.SetLabel(f"Selected: {selected_label}")
        self.selection_summary.Centre(wx.HORIZONTAL)

        if not requested_patchset:
            status = "Select at least one applicable root patch."
        elif root_state.state != RootPatchState.CLEAN:
            status = root_state.reason
        elif detection.can_patch is False:
            status = "The selected root patches cannot be applied with the current system requirements."
        else:
            status = "Ready to apply the selected root patches."
        self.selection_state_label.SetLabel(status)
        self.selection_state_label.Wrap(330)
        self.selection_state_label.Centre(wx.HORIZONTAL)

        start_allowed = bool(requested_patchset) and detection.can_patch and root_state.patch_allowed
        self.start_button.Enable(start_allowed)
        if start_allowed:
            self.start_button.SetDefault()
        self.revert_button.Enable(root_state.revert_allowed(detection.can_unpatch))
        self.available_patches = start_allowed


    def on_patch_selection_changed(self, identifier: SelectableRootPatch, selected: bool) -> None:
        self.selection = self.selection.with_selection(identifier, selected)
        self._refresh_selection_state()
        self.frame_modal.Layout()


    def on_start_root_patching(self, event: wx.Event = None):
        self._refresh_selection_state()
        if not self.requested_patchset:
            wx.MessageBox("Select at least one applicable root patch.", "Root Patching Blocked", wx.OK | wx.ICON_WARNING)
            return
        if self.current_detection.can_patch is False:
            wx.MessageBox(
                "The selected root patches cannot be applied with the current system requirements.",
                "Root Patching Blocked",
                wx.OK | wx.ICON_WARNING,
            )
            return
        if self.root_state.patch_allowed is False:
            logging.error(self.root_state.reason)
            wx.MessageBox(self.root_state.reason, "Root Patching Blocked", wx.OK | wx.ICON_WARNING)
            return
        frame = gui_sys_patch_start.SysPatchStartFrame(
            parent=None,
            title=self.title,
            global_constants=self.constants,
            patches=self.current_detection.device_properties,
        )
        self.frame_modal.Hide()
        self.frame_modal.Destroy()
        self.frame.Hide()
        self.frame.Destroy()
        frame.start_root_patching()


    def on_revert_root_patching(self, event: wx.Event = None):
        self._refresh_selection_state()
        if self.root_state.revert_allowed(self.current_detection.can_unpatch) is False:
            logging.error(self.root_state.reason)
            wx.MessageBox(self.root_state.reason, "Root Patch Reversion Unavailable", wx.OK | wx.ICON_WARNING)
            return
        frame = gui_sys_patch_start.SysPatchStartFrame(
            parent=None,
            title=self.title,
            global_constants=self.constants,
            patches=self.current_detection.device_properties,
        )
        self.frame_modal.Hide()
        self.frame_modal.Destroy()
        self.frame.Hide()
        self.frame.Destroy()
        frame.revert_root_patching()


    def on_return_to_main_menu(self, event: wx.Event = None):
        # Get frame from event
        frame_modal: wx.Dialog = event.GetEventObject().GetParent()
        frame: wx.Frame = frame_modal.Parent
        frame_modal.Hide()
        frame.Hide()

        main_menu_frame = gui_main_menu.MainFrame(
            None,
            title=self.title,
            global_constants=self.constants,
        )
        main_menu_frame.Show()
        frame.Destroy()


    def on_return_dismiss(self, event: wx.Event = None):
        self.frame_modal.Hide()
        self.frame_modal.Destroy()
