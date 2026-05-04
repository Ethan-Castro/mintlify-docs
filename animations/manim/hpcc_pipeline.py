"""HPCC pipeline animation (light theme).

Renders a ~40 second 1080p MP4 narrating the CSI HPCC data-staging and SLURM
execution pipeline as a clean horizontal flow of seven cards on a white
background. Designed to read like an institutional explainer slide.

Manim 0.20.1. Avoids known bugs:
  - No `Arrow` / `GrowArrow` (broken in 0.20.1: `.hex` AttributeError).
  - All hex colors wrapped in `ManimColor("#...")` before use.
  - No `LaggedStartMap` over containers; uses explicit per-mobject animations.
"""

from __future__ import annotations

import sys
from typing import Dict, List

import numpy as np
from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    AnimationGroup,
    Create,
    DashedVMobject,
    FadeIn,
    FadeOut,
    Line,
    ManimColor,
    MoveAlongPath,
    RoundedRectangle,
    Scene,
    Text,
    VGroup,
    Write,
    config,
)

# ---------------------------------------------------------------------------
# Module-level configuration
# ---------------------------------------------------------------------------

LOW_MOTION: bool = False

# Light theme palette ------------------------------------------------------
BG_COLOR = ManimColor("#ffffff")
TEXT_PRIMARY = ManimColor("#0f172a")  # near-black navy
TEXT_MUTED = ManimColor("#64748b")    # slate
ACCENT = ManimColor("#7abde8")        # CSI HPCC primary blue
CARD_FILL = ManimColor("#f8fafc")
CARD_STROKE = ManimColor("#e5e7eb")

DURABLE_STROKE = ManimColor("#16a34a")   # green for home/archive
SCRATCH_STROKE = ManimColor("#d97706")   # amber for scratch
COMPUTE_STROKE = ManimColor("#1f4f7a")   # deep navy for compute

EDGE_COLOR = ManimColor("#cbd5e1")       # light grey connector

config.background_color = BG_COLOR
config.frame_rate = 60
config.pixel_width = 1920
config.pixel_height = 1080

# ---------------------------------------------------------------------------
# Pipeline data
# ---------------------------------------------------------------------------

PIPELINE = {
    "stages": [
        {"id": "workstation", "label": "Workstation",       "sub": "your laptop"},
        {"id": "transfer",    "label": "Transfer",          "sub": "Globus / SFTP"},
        {"id": "home",        "label": "Home",              "sub": "/global/u/<id>"},
        {"id": "scratch",     "label": "Scratch",           "sub": "/scratch/<id>"},
        {"id": "slurm",       "label": "SLURM queue",       "sub": "wait for nodes"},
        {"id": "compute",     "label": "Arrow compute",     "sub": "CPU + GPU"},
        {"id": "archive",     "label": "Archive",           "sub": "long-term"},
    ],
    "flows": [
        ("workstation", "transfer"),
        ("transfer",    "home"),
        ("home",        "scratch"),
        ("scratch",     "slurm"),
        ("slurm",       "compute"),
        ("compute",     "home"),
        ("compute",     "archive"),
    ],
    "narration": [
        "You upload code and data from your laptop.",
        "Globus or SFTP moves the files onto the cluster.",
        "Files land in your durable home directory — backed up, slow.",
        "You stage the files into scratch — fast NVMe, no backup.",
        "You submit the job; SLURM queues it until nodes are free.",
        "SLURM places the job on Arrow's CPU or GPU nodes.",
        "Outputs go back to home; long-term results to archive.",
    ],
}

# Per-stage stroke override; falls back to neutral CARD_STROKE.
STAGE_STROKE: Dict[str, ManimColor] = {
    "home": DURABLE_STROKE,
    "scratch": SCRATCH_STROKE,
    "slurm": ACCENT,
    "compute": COMPUTE_STROKE,
    "archive": DURABLE_STROKE,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rt(value: float) -> float:
    """Return value, or near-zero when LOW_MOTION is set."""
    return 0.05 if LOW_MOTION else value


def _make_card(stage: dict, width: float, height: float) -> VGroup:
    """A rounded white-ish card with a label and a muted sub-label."""
    stage_id = stage["id"]
    stroke_color = STAGE_STROKE.get(stage_id, CARD_STROKE)
    stroke_width = 2.2 if stage_id in STAGE_STROKE else 1.5

    box = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.16,
        color=stroke_color,
        fill_color=CARD_FILL,
        fill_opacity=1.0,
        stroke_width=stroke_width,
    )

    # Scratch gets a dashed border to telegraph "ephemeral".
    if stage_id == "scratch":
        dashed = DashedVMobject(
            RoundedRectangle(
                width=width,
                height=height,
                corner_radius=0.16,
                color=SCRATCH_STROKE,
                stroke_width=2.2,
                fill_opacity=0,
            ),
            num_dashes=44,
            dashed_ratio=0.55,
        )
        # Replace the solid border visually by setting the base box stroke very light.
        box.set_stroke(SCRATCH_STROKE, width=0, opacity=0)
        border = dashed
    else:
        border = VGroup()  # placeholder

    label = Text(stage["label"], font_size=28, color=TEXT_PRIMARY, weight="MEDIUM")
    sub = Text(stage["sub"], font_size=18, color=TEXT_MUTED)

    # Fit the label/sub-label inside the card.
    max_text_width = width - 0.25
    if label.width > max_text_width:
        label.scale_to_fit_width(max_text_width)
    if sub.width > max_text_width:
        sub.scale_to_fit_width(max_text_width)

    text_block = VGroup(label, sub).arrange(DOWN, buff=0.08)
    text_block.move_to(box.get_center())

    return VGroup(box, border, text_block)


def _packet(color: ManimColor = ACCENT) -> RoundedRectangle:
    return RoundedRectangle(
        width=0.28,
        height=0.28,
        corner_radius=0.06,
        color=color,
        fill_color=color,
        fill_opacity=1.0,
        stroke_width=0,
    )


# ---------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------

class HPCCPipeline(Scene):
    """Light-theme HPCC data-staging + SLURM pipeline."""

    def construct(self) -> None:  # noqa: C901 - long but linear
        # --- Validate JSON ------------------------------------------------
        stage_ids = {s["id"] for s in PIPELINE["stages"]}
        for src, tgt in PIPELINE["flows"]:
            assert src in stage_ids, f"flow source {src!r} not in stages"
            assert tgt in stage_ids, f"flow target {tgt!r} not in stages"
        assert len(PIPELINE["narration"]) == len(PIPELINE["stages"]), (
            "narration count must match stage count"
        )

        flows_animated = 0
        stages_shown = 0

        # --- Title --------------------------------------------------------
        title = Text(
            "CSI HPCC Pipeline",
            font_size=42,
            color=TEXT_PRIMARY,
            weight="BOLD",
        )
        subtitle = Text(
            "From your laptop to Arrow compute and back",
            font_size=22,
            color=TEXT_MUTED,
        )
        title.to_edge(UP, buff=0.55)
        subtitle.next_to(title, DOWN, buff=0.18)

        self.play(Write(title, run_time=_rt(0.9)))
        self.play(FadeIn(subtitle, run_time=_rt(0.4)))
        self.wait(_rt(0.3))

        # --- Layout 7 cards in a single horizontal row --------------------
        n = len(PIPELINE["stages"])
        # Frame is ~14.22 wide at 16:9. Use 13.4 of it for the row.
        row_width = 13.4
        card_width = 1.70
        card_height = 1.45
        gap = (row_width - n * card_width) / (n - 1)
        row_y = 0.4

        cards: Dict[str, VGroup] = {}
        for i, stage in enumerate(PIPELINE["stages"]):
            x = -row_width / 2 + card_width / 2 + i * (card_width + gap)
            card = _make_card(stage, card_width, card_height)
            card.move_to(np.array([x, row_y, 0.0]))
            cards[stage["id"]] = card

        # Anchor points for connector lines (right edge -> left edge).
        anchors_right: Dict[str, np.ndarray] = {}
        anchors_left: Dict[str, np.ndarray] = {}
        for sid, card in cards.items():
            box = card[0]
            anchors_right[sid] = box.get_right()
            anchors_left[sid] = box.get_left()

        # --- Reveal cards left-to-right -----------------------------------
        card_intros = [FadeIn(cards[s["id"]], shift=UP * 0.12) for s in PIPELINE["stages"]]
        self.play(
            AnimationGroup(*card_intros, lag_ratio=0.07),
            run_time=_rt(1.4),
        )
        stages_shown = n

        # --- Connector lines between adjacent cards in the row ------------
        connectors: List[Line] = []
        for i in range(n - 1):
            src_id = PIPELINE["stages"][i]["id"]
            tgt_id = PIPELINE["stages"][i + 1]["id"]
            start = anchors_right[src_id] + np.array([0.04, 0.0, 0.0])
            end = anchors_left[tgt_id] + np.array([-0.04, 0.0, 0.0])
            line = Line(start=start, end=end, color=EDGE_COLOR, stroke_width=2.2)
            connectors.append(line)

        self.play(
            AnimationGroup(*[Create(c) for c in connectors], lag_ratio=0.06),
            run_time=_rt(0.9),
        )

        # --- Narration line at bottom -------------------------------------
        narration_y = -3.05
        narration = Text(
            PIPELINE["narration"][0],
            font_size=24,
            color=TEXT_PRIMARY,
        )
        narration.move_to(np.array([0.0, narration_y, 0.0]))
        # Cap width so long sentences never spill off-screen.
        max_narr_width = 12.5
        if narration.width > max_narr_width:
            narration.scale_to_fit_width(max_narr_width)

        # Stage indicator (small "Step k of 7" pill above narration).
        step_label = Text(
            f"Step 1 of {n}",
            font_size=18,
            color=TEXT_MUTED,
        )
        step_label.move_to(np.array([0.0, narration_y + 0.55, 0.0]))

        self.play(
            FadeIn(step_label, run_time=_rt(0.3)),
            FadeIn(narration, run_time=_rt(0.4)),
        )

        def update_narration(step_idx: int, message: str) -> None:
            new_step = Text(
                f"Step {step_idx + 1} of {n}",
                font_size=18,
                color=TEXT_MUTED,
            )
            new_step.move_to(np.array([0.0, narration_y + 0.55, 0.0]))

            new_text = Text(message, font_size=24, color=TEXT_PRIMARY)
            if new_text.width > max_narr_width:
                new_text.scale_to_fit_width(max_narr_width)
            new_text.move_to(np.array([0.0, narration_y, 0.0]))

            if LOW_MOTION:
                step_label.become(new_step)
                narration.become(new_text)
            else:
                self.play(
                    FadeOut(narration, run_time=0.18),
                    FadeOut(step_label, run_time=0.18),
                    run_time=0.18,
                )
                step_label.become(new_step)
                narration.become(new_text)
                self.play(
                    FadeIn(step_label, run_time=0.22),
                    FadeIn(narration, run_time=0.22),
                )

        # --- Highlight the active card by darkening its stroke briefly ----
        def highlight(stage_id: str, run_time: float = 0.35) -> None:
            card = cards[stage_id]
            box = card[0]
            original_stroke = box.get_stroke_color()
            original_width = box.get_stroke_width()
            self.play(
                box.animate.set_stroke(ACCENT, width=3.5),
                run_time=_rt(run_time),
            )
            self.play(
                box.animate.set_stroke(original_stroke, width=original_width),
                run_time=_rt(run_time * 0.8),
            )

        # --- Walk a single packet through the row -------------------------
        # We narrate per stage (7 narrations). The packet hops along the 6
        # row connectors, with extra business at scratch and slurm.
        # Mapping: narration[i] is shown WHILE the packet sits at / arrives at
        # stage i. The first narration shows with the packet at workstation;
        # then the packet hops across each connector and we update narration.

        # Place the packet at the first card.
        packet = _packet(ACCENT)
        packet.move_to(cards["workstation"][0].get_center())
        self.play(FadeIn(packet, run_time=_rt(0.35)))
        highlight("workstation", run_time=0.3)
        self.wait(_rt(2.6))  # let the viewer read narration 1

        # Hop through the row: workstation -> transfer -> home -> scratch ->
        # slurm -> compute -> archive (the row order, which matches stages).
        flow_index = 0
        # Reusable per-hop run_time so total ~= 40s.
        HOP_TIME = 1.0
        DWELL_TIME = 2.4

        def hop(from_id: str, to_id: str, narration_idx: int) -> None:
            nonlocal flow_index
            # Build a path along the connector between adjacent cards.
            start = cards[from_id][0].get_center()
            end = cards[to_id][0].get_center()
            # Offset: travel along the connector line height, not card center.
            start_anchor = np.array([anchors_right[from_id][0] + 0.04, row_y, 0.0])
            end_anchor = np.array([anchors_left[to_id][0] - 0.04, row_y, 0.0])

            # Move packet to the row-line height first if needed.
            move_path = Line(start=packet.get_center(), end=start_anchor)
            self.play(MoveAlongPath(packet, move_path, run_time=_rt(0.25)))

            travel_path = Line(start=start_anchor, end=end_anchor)
            self.play(MoveAlongPath(packet, travel_path, run_time=_rt(HOP_TIME)))

            # Slide packet onto the next card center.
            settle_path = Line(start=end_anchor, end=cards[to_id][0].get_center())
            self.play(MoveAlongPath(packet, settle_path, run_time=_rt(0.25)))

            update_narration(narration_idx, PIPELINE["narration"][narration_idx])
            highlight(to_id, run_time=0.3)
            flow_index += 1

        # narration[0] already shown for workstation. Now hop step by step.
        # transfer
        hop("workstation", "transfer", 1)
        self.wait(_rt(DWELL_TIME))
        flows_animated += 1

        # home (durable)
        hop("transfer", "home", 2)
        self.wait(_rt(DWELL_TIME))
        flows_animated += 1

        # scratch (ephemeral, strobe amber to convey impermanence)
        hop("home", "scratch", 3)
        scratch_box = cards["scratch"][0]
        # Two soft pulses on the scratch fill.
        for _ in range(2):
            self.play(
                scratch_box.animate.set_fill(ManimColor("#fef3c7"), opacity=1.0),
                packet.animate.set_opacity(0.35),
                run_time=_rt(0.35),
            )
            self.play(
                scratch_box.animate.set_fill(CARD_FILL, opacity=1.0),
                packet.animate.set_opacity(1.0),
                run_time=_rt(0.35),
            )
        self.wait(_rt(DWELL_TIME - 0.6))
        flows_animated += 1

        # slurm queue (queueing cue)
        hop("scratch", "slurm", 4)
        # Show three small grey queued packets stacking up under the slurm card.
        queued = VGroup(
            *[
                RoundedRectangle(
                    width=0.22,
                    height=0.22,
                    corner_radius=0.05,
                    color=TEXT_MUTED,
                    fill_color=TEXT_MUTED,
                    fill_opacity=0.55,
                    stroke_width=0,
                )
                for _ in range(3)
            ]
        )
        queued.arrange(RIGHT, buff=0.1)
        queued.next_to(cards["slurm"][0], DOWN, buff=0.18)
        self.play(
            AnimationGroup(*[FadeIn(q) for q in queued], lag_ratio=0.18),
            run_time=_rt(0.7),
        )
        self.wait(_rt(DWELL_TIME - 0.4))
        self.play(FadeOut(queued, run_time=_rt(0.35)))
        flows_animated += 1

        # compute
        hop("slurm", "compute", 5)
        # Small "processing" pulse on the compute card.
        compute_box = cards["compute"][0]
        self.play(
            compute_box.animate.set_stroke(COMPUTE_STROKE, width=4.0),
            run_time=_rt(0.35),
        )
        self.play(
            compute_box.animate.set_stroke(COMPUTE_STROKE, width=2.2),
            run_time=_rt(0.35),
        )
        self.wait(_rt(DWELL_TIME - 0.5))
        flows_animated += 1

        # archive (final stage)
        hop("compute", "archive", 6)
        # The narration covers "outputs go back to home; long-term to archive".
        # Briefly highlight home then settle on archive.
        home_box = cards["home"][0]
        self.play(
            home_box.animate.set_stroke(ACCENT, width=3.5),
            run_time=_rt(0.4),
        )
        self.play(
            home_box.animate.set_stroke(DURABLE_STROKE, width=2.2),
            run_time=_rt(0.4),
        )
        self.wait(_rt(DWELL_TIME))
        # Final hop counts as the compute->archive flow (+1) AND we visualized
        # the compute->home flow via the home-card highlight pulse above (+1).
        flows_animated += 2

        # --- Outro --------------------------------------------------------
        self.play(FadeOut(packet, run_time=_rt(0.4)))
        self.wait(_rt(0.6))

        # Stderr summary for the caller.
        print(
            f"[HPCCPipeline] flows_animated={flows_animated} stages_shown={stages_shown}",
            file=sys.stderr,
        )
