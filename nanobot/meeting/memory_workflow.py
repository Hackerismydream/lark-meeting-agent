"""Memory consolidation workflow for completed meetings."""

from __future__ import annotations

from pathlib import Path

from nanobot.meeting.memory import MeetingMemoryStore
from nanobot.meeting.schemas import EntityMemory, MemoryEntityType, Run


class MemoryWorkflow:
    def __init__(self, workspace: Path | str) -> None:
        self.store = MeetingMemoryStore(workspace)

    def consolidate_run(self, run: Run) -> list[str]:
        paths: list[str] = []
        if not run.meeting or not run.minutes:
            return paths
        for action in run.minutes.action_items:
            owner = action.owner
            if owner:
                paths.append(
                    self.store.persist_entity_memory(
                        EntityMemory(
                            entity_type=MemoryEntityType.PERSON,
                            entity_id=owner.lower(),
                            name=owner,
                            summary=f"{owner} committed: {action.task}",
                            source_meeting_ids=[run.meeting.meeting_id],
                            source_segment_ids=[e.segment_id for e in action.evidence_refs],
                        )
                    )
                )
        project_hint = run.meeting.title
        if run.minutes.decisions:
            paths.append(
                self.store.persist_entity_memory(
                    EntityMemory(
                        entity_type=MemoryEntityType.PROJECT,
                        entity_id=project_hint.lower().replace(" ", "-"),
                        name=project_hint,
                        summary="；".join(decision.text for decision in run.minutes.decisions[:3]),
                        source_meeting_ids=[run.meeting.meeting_id],
                        source_segment_ids=[e.segment_id for decision in run.minutes.decisions for e in decision.evidence_refs],
                    )
                )
            )
        return paths
