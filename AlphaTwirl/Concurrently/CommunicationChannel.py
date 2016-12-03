# Tai Sakuma <tai.sakuma@cern.ch>
import multiprocessing
import logging
from operator import itemgetter

from ..ProgressBar import NullProgressMonitor
from .TaskPackage import TaskPackage

from .Worker import Worker

##__________________________________________________________________||
class TaskPackageDropbox(object):
    def __init__(self, nprocesses = 16, progressMonitor = None):

        if nprocesses <= 0:
            raise ValueError("nprocesses must be at least one: {} is given".format(nprocesses))

        self.progressMonitor = NullProgressMonitor() if progressMonitor is None else progressMonitor

        self.n_max_workers = nprocesses
        self.n_workers = 0
        self.task_queue = multiprocessing.JoinableQueue()
        self.result_queue = multiprocessing.Queue()
        self.lock = multiprocessing.Lock()
        self.n_ongoing_tasks = 0
        self.task_idx = -1 # so it starts from 0

    def open(self):

        if self.n_workers >= self.n_max_workers:
            # workers already created
            return

        # start workers
        for i in xrange(self.n_workers, self.n_max_workers):
            worker = Worker(
                task_queue = self.task_queue,
                result_queue = self.result_queue,
                progressReporter = self.progressMonitor.createReporter(),
                lock = self.lock
            )
            worker.start()
            self.n_workers += 1

    def put(self, package):
        self.task_idx += 1
        self.task_queue.put((self.task_idx, package.task, package.args, package.kwargs))
        self.n_ongoing_tasks += 1

    def receive(self):
        messages = [ ] # a list of (task_idx, result)
        while self.n_ongoing_tasks >= 1:
            if self.result_queue.empty(): continue
            message = self.result_queue.get()
            messages.append(message)
            self.n_ongoing_tasks -= 1

        # sort in the order of task_idx
        messages = sorted(messages, key = itemgetter(0))

        results = [result for task_idx, result in messages]
        return results

    def close(self):
        for i in xrange(self.n_workers):
            self.task_queue.put(None) # end workers
        self.task_queue.join()
        self.n_workers = 0

##__________________________________________________________________||
class CommunicationChannel(object):
    """A communication channel with workers in other processes.

    You can send tasks to workers through this channel. The workers,
    running in other processes, execute the tasks in the background.
    You can receive the results of the tasks also through this
    channel.

    An instance of this class can be created with two optional
    arguments: ``nprocesses``, the number of workers to be created,
    and ``progressMonitor``::

        progressBar = ProgressBar()
        progressMonitor = BProgressMonitor(progressBar)
        channel = CommunicationChannel(nprocesses = 10, progressMonitor = progressMonitor)

    Workers will be created when ``begin()`` is called::

        channel.begin()

    In ``begin()``, this class gives each worker a
    ``progressReporter``, which is created by the ``progressMonitor``.

    Now, you are ready to send a task. A task is a function or any
    object which is callable and picklable. A task can take any number
    of arguments. If a task takes a named argument
    ``progressReporter``, the worker will give the
    ``progressReporter`` to the task. A value that a task returns is
    the result of the task and must be picklable. For example, an
    instance of ``EventLoop`` can be a task. You can send a task with
    the method ``put``::

        channel.put(task1, 10, 20, A = 30)

    Here, 10, 20, A = 30 are the arguments to the task.

    This class sends the task to a worker. The worker which receives
    the task will first try to call the task with the
    ``progressReporter`` in addition to the arguments. If the task
    doesn't take the ``progressReporter``, it calls only with the
    arguments.

    You can send multiple tasks::

        channel.put(task2)
        channel.put(task3, 100, 200)
        channel.put(task4, A = 'abc')
        channel.put(task5)

    They will be executed by workers.

    You can receive the results of the tasks with the method
    ``receive()``::

        results = channel.receive()

    This method will wait until all tasks are finished. If a task
    gives a ``progressReport`` to the ``progressReporter``, the report
    will be used, for example, to update progress bars on the screen.

    When all tasks end, results will be returned. The return value
    ``results`` is a list of results of the tasks. They are sorted in
    the order in which the tasks are originally put.

    After receiving the results, you can put more tasks::

        channel.put(task6)
        channel.put(task7)

    And you can receive the results of them::

        results = channel.receive()

    If there are no more tasks to be done, you should call the method
    ``end``::

        channel.end()

    This will end all background processes.

    """

    def __init__(self, nprocesses = 16, progressMonitor = None):
        progressMonitor = NullProgressMonitor() if progressMonitor is None else progressMonitor
        self.progressMonitor = progressMonitor
        self.dropbox = TaskPackageDropbox(
            nprocesses = nprocesses,
            progressMonitor = progressMonitor
        )
        self.isopen = False

    def begin(self):
        if self.isopen: return
        self.dropbox.open()
        self.isopen = True

    def put(self, task, *args, **kwargs):
        if not self.isopen:
            logger = logging.getLogger(__name__)
            logger.warning('the drop box is not open')
            return

        package = TaskPackage(
            task = task,
            args = args,
            kwargs =  kwargs
        )
        self.dropbox.put(package)

    def receive(self):
        if not self.isopen:
            logger = logging.getLogger(__name__)
            logger.warning('the drop box is not open')
            return

        results = self.dropbox.receive()
        return results

    def end(self):
        if not self.isopen: return
        self.dropbox.close()
        self.isopen = False

##__________________________________________________________________||
