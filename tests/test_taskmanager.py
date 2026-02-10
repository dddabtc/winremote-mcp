"""Unit tests for TaskManager concurrency/cancellation logic."""

from __future__ import annotations

from winremote.taskmanager import TaskManager, TaskStatus, ToolCategory


class TestTaskManager:
    def setup_method(self):
        self.tm = TaskManager()

    def test_create_task(self):
        task = self.tm.create_task("Click")
        assert task.tool_name == "Click"
        assert task.category == ToolCategory.DESKTOP
        assert task.status == TaskStatus.PENDING

    def test_cancel_task(self):
        task = self.tm.create_task("Shell")
        result = self.tm.cancel_task(task.task_id)
        assert result["status"] == "cancelled"
        assert task.status == TaskStatus.CANCELLED

    def test_cancel_nonexistent(self):
        result = self.tm.cancel_task("doesnotexist")
        assert "error" in result

    def test_cancel_completed_task(self):
        task = self.tm.create_task("Ping")
        task.status = TaskStatus.COMPLETED
        result = self.tm.cancel_task(task.task_id)
        assert "error" in result

    def test_list_tasks(self):
        self.tm.create_task("Click")
        self.tm.create_task("Shell")
        tasks = self.tm.list_tasks()
        assert len(tasks) == 2

    def test_list_tasks_filter(self):
        t1 = self.tm.create_task("Click")
        t1.status = TaskStatus.RUNNING
        t2 = self.tm.create_task("Shell")
        t2.status = TaskStatus.COMPLETED
        running = self.tm.list_tasks("running")
        assert len(running) == 1
        assert running[0]["tool_name"] == "Click"

    def test_get_task(self):
        task = self.tm.create_task("Snapshot")
        info = self.tm.get_task(task.task_id)
        assert info is not None
        assert info["tool_name"] == "Snapshot"

    def test_get_task_not_found(self):
        assert self.tm.get_task("nope") is None

    def test_wrap_sync_tool(self):
        def my_tool(x):
            return f"result={x}"

        wrapped = self.tm.wrap_sync_tool("Click", my_tool)
        result = wrapped(42)
        assert "result=42" in result
        assert "task:" in result

    def test_wrap_sync_tool_error(self):
        def bad_tool():
            raise RuntimeError("boom")

        wrapped = self.tm.wrap_sync_tool("Shell", bad_tool)
        result = wrapped()
        assert "Error" in result
        assert "boom" in result

    def test_task_duration(self):
        import time
        task = self.tm.create_task("Wait")
        task.started_at = time.time() - 2.0
        task.completed_at = time.time()
        assert task.duration is not None
        assert task.duration >= 1.5

    def test_tool_categories(self):
        from winremote.taskmanager import TOOL_CATEGORIES
        assert TOOL_CATEGORIES["Click"] == ToolCategory.DESKTOP
        assert TOOL_CATEGORIES["Shell"] == ToolCategory.SHELL
        assert TOOL_CATEGORIES["Ping"] == ToolCategory.NETWORK
        assert TOOL_CATEGORIES["FileRead"] == ToolCategory.FILE
