from collections.abc import Callable

import wakaq
from attr import field, mutable
from flask import Flask


@mutable
class WakaQ:
    app: Flask | None = None

    _wakaq: wakaq.WakaQ | None = field(default=None, init=False)
    _jobs: list = field(factory=list, init=False)

    def __attrs_post_init__(self):
        if self.app is not None:
            self.init_app(self.app)

    def init_app(self, app: Flask):
        if "wakaq" in app.extensions:
            raise RuntimeError(
                "This extension is already registered on this Flask app."
            )

        app.extensions["wakaq"] = self

        # if app.config["MOCK_WAKAQ"]:
        #     return WakaQMock()

        # priority = wakaq.utils.get_worker_priority()
        # exclude_queues = WORKER_PRIORITIES[priority]

        _wakaq = wakaq.WakaQ(["low", "high", "default"])

        # _wakaq = wakaq.WakaQ(
        #     queues=app.config["QUEUES"],
        #     host=app.config["WAKAQ_HOST"],
        #     worker_log_file="/var/log/wakaq/worker.log",
        #     # worker_log_level=logging.DEBUG,
        #     scheduler_log_file="/var/log/wakaq/scheduler.log",
        #     soft_timeout=app.config["WAKAQ_SOFT_TIMEOUT_TD"],
        #     hard_timeout=app.config["WAKAQ_HARD_TIMEOUT_TD"],
        #     max_retries=1,
        #     concurrency="cores*6",
        #     max_mem_percent=95,
        #     schedules=app.config["WAKAQ_SCHEDULED_TASKS"],
        #     socket_connect_timeout=30 if app.config["IS_WORKER"] else 1,
        #     socket_timeout=30 if app.config["IS_WORKER"] else 3,
        #     # exclude_queues=exclude_queues,
        # )

        @_wakaq.wrap_tasks_with
        def custom_task_decorator(fn):
            def inner(*args, **kwargs):
                with app.app_context():
                    return fn(*args, **kwargs)

            return inner

        self._wakaq = _wakaq

        for fn, kwargs in self._jobs:
            task = self._wakaq.task(fn, **kwargs)
            fn.delay = task.delay
            fn.broadcast = task.broadcast

        self._jobs = []

    def task(self, fn: Callable | None = None, **kwargs) -> Callable:
        def wrap(fn):
            if self._wakaq:
                return self._wakaq.task(fn, **kwargs)
            else:
                self._jobs.append((fn, kwargs))
                return fn

        if fn:
            return wrap(fn)
        else:
            return wrap
