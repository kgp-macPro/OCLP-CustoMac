"""Native dialog for operation-scoped manual Kernel Debug Kit selection."""

from __future__ import annotations

import wx

from ..support.kdk_selection import (
    KDKCandidateStatus,
    KDKSelectionContext,
    KernelDebugKitCandidate,
)
from . import gui_support


def candidate_status_text(status: KDKCandidateStatus) -> str:
    match = "Exact Match" if status.automatic_exact_match else "Closest Match" if status.automatic_choice else ""
    installed = "Installed" if status.installed else "Not Installed"
    automatic = "OCLP Automatic Choice" if status.automatic_choice else ""
    return " · ".join(item for item in (match, installed, automatic) if item)


def candidate_display_text(status: KDKCandidateStatus) -> str:
    candidate = status.candidate
    return f"macOS {candidate.version} — Build {candidate.build} — {candidate_status_text(status)}"


def automatic_choice_text(context: KDKSelectionContext) -> str:
    candidate = context.automatic_candidate
    if candidate is None:
        return "OCLP automatic selection:\nNo eligible automatic KDK selection is available."
    status = context.status_for(candidate)
    if status is None:
        return "OCLP automatic selection:\nNo eligible automatic KDK selection is available."
    return (
        "OCLP automatic selection:\n"
        f"macOS {candidate.version} — Build {candidate.build}\n"
        f"{candidate_status_text(status)}"
    )


class ManualKDKSelectionDialog(wx.Dialog):
    """Select and explicitly confirm one trusted catalog candidate."""

    def __init__(self, parent: wx.Window, context: KDKSelectionContext):
        super().__init__(parent, title="Select Kernel Debug Kit", size=(520, 430))
        self.context = context
        self.selected_candidate: KernelDebugKitCandidate | None = None

        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(panel, label="Select Kernel Debug Kit")
        title.SetFont(gui_support.font_factory(19, wx.FONTWEIGHT_BOLD))
        outer.Add(title, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 16)

        description = wx.StaticText(
            panel,
            label="Choose one official macOS Tahoe KDK for this patch operation.",
        )
        description.SetFont(gui_support.font_factory(12, wx.FONTWEIGHT_NORMAL))
        outer.Add(description, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP | wx.LEFT | wx.RIGHT, 8)

        automatic = wx.StaticText(panel, label=automatic_choice_text(context))
        automatic.SetFont(gui_support.font_factory(12, wx.FONTWEIGHT_BOLD))
        outer.Add(automatic, 0, wx.EXPAND | wx.ALL, 14)

        self.candidate_list = wx.ListBox(
            panel,
            choices=[candidate_display_text(status) for status in context.candidates],
            style=wx.LB_SINGLE | wx.LB_NEEDED_SB,
            size=(-1, 210),
        )
        outer.Add(self.candidate_list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 14)

        buttons = wx.StdDialogButtonSizer()
        cancel_button = wx.Button(panel, wx.ID_CANCEL, "Cancel")
        confirm_button = wx.Button(panel, wx.ID_OK, "Use This KDK")
        confirm_button.Bind(wx.EVT_BUTTON, self._on_confirm)
        buttons.AddButton(cancel_button)
        buttons.AddButton(confirm_button)
        buttons.Realize()
        outer.Add(buttons, 0, wx.ALIGN_RIGHT | wx.ALL, 14)

        panel.SetSizer(outer)
        self.CentreOnParent()

    def _on_confirm(self, event: wx.Event) -> None:
        selection = self.candidate_list.GetSelection()
        if selection == wx.NOT_FOUND:
            wx.MessageBox(
                "Select a Kernel Debug Kit before continuing.",
                "Kernel Debug Kit Required",
                wx.OK | wx.ICON_WARNING,
                parent=self,
            )
            return

        status = self.context.candidates[selection]
        candidate = status.candidate
        message = (
            "Selected Kernel Debug Kit:\n"
            f"macOS {candidate.version}\n"
            f"Build {candidate.build}\n"
            f"Status: {'Installed' if status.installed else 'Not Installed'}"
        )
        if self.context.automatic_candidate not in (None, candidate):
            automatic = self.context.automatic_candidate
            message += f"\n\nOCLP automatic choice: macOS {automatic.version} — Build {automatic.build}"
        confirmation = wx.MessageDialog(
            self,
            message,
            "Confirm Kernel Debug Kit",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_INFORMATION,
        )
        confirmation.SetYesNoLabels("Use This KDK", "Cancel")
        if confirmation.ShowModal() != wx.ID_YES:
            return

        self.selected_candidate = candidate
        self.EndModal(wx.ID_OK)

    def select_candidate(self) -> KernelDebugKitCandidate | None:
        if self.ShowModal() != wx.ID_OK:
            return None
        return self.selected_candidate
