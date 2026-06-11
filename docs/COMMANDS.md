# Commands

## Canonical Commands

```text
/meeting process [query]
/meeting prebrief [query]
/meeting status [run_id]
/meeting qa <question>
/meeting approve <run_id> <operation_id> [operation_id...]
/meeting reject <run_id>
/meeting live-join <9-digit-meeting-number> --approve-visible-join
/meeting live-leave <meeting_id> --approve-visible-leave
/meeting live-qa <live_run_id> <question>
```

## Chinese Aliases

```text
整理最近一场会
帮我准备 <会议/项目>
查看待审批操作
查询：<问题>
加入会议 <9位会议号>
离开会议 <meeting_id>
```

## Approval Flow

`/meeting process` returns a dry-run preview. It lists the `run_id` and operation IDs. No Lark write happens until an approver sends `/meeting approve`.

`/meeting status` without a `run_id` lists recent pending approval runs.

## Live Flow

Joining and leaving are visible to meeting participants. The bot returns `approval_required` unless the command includes the explicit visible approval flag and the sender is a live approver or admin.
