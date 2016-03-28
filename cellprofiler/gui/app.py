import os
import pip
import platform
import raven
import sys
import wx
import cellprofiler.preferences
import cellprofiler.gui.errordialog
import cellprofiler.utilities.thread_excepthook


cellprofiler.utilities.thread_excepthook.install_thread_sys_excepthook()


class App(wx.App):
    def __excepthook__(self, exception, message, tracback):
        def callback():
            self.client.captureException(
                exc_info=(exception, message, tracback)
            )

            cellprofiler.preferences.cancel_progress()

            cellprofiler.gui.errordialog.display_error_dialog(self.frame, message, None, tb=tracback, continue_only=True, message="Exception in CellProfiler core processing")

        wx.CallAfter(callback)

    def __init__(self, *args, **kwargs):
        self.abort_initialization = False

        self.check_for_new_version = kwargs.pop('check_for_new_version', False)

        path = os.path.join(os.path.dirname(__file__), os.pardir)

        try:
            release = raven.fetch_git_sha(path)
        except raven.versioning.InvalidGitRepository:
            release = raven.fetch_package_version("cellprofiler")

        self.client = raven.Client(
            dsn="https://3d53494dbaaf4e858afd79f56506a749:8a7a767a1924423f89c1fdfd69717fd5@app.getsentry.com/70887",
            release=release,
        )

        self.client.user_context({
            "installed_distributions": sorted([
                "{0:s}=={1:s}".format(
                    distribution.key, distribution.version
                ) for distribution in pip.get_installed_distributions()
            ]),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "release": platform.release(),
            "system": platform.system(),
            "version": platform.version(),
        })

        self.frame = None

        self.pipeline_path = kwargs.pop('pipeline_path', None)

        self.workspace_path = kwargs.pop('workspace_path', None)

        super(App, self).__init__(*args, **kwargs)

    def OnInit(self):
        import cellprofiler.gui.cpframe

        self.SetAppName(
            u"CellProfiler{0:s}".format(
                cellprofiler.utilities.version.dotted_version
            )
        )

        self.frame = cellprofiler.gui.cpframe.CPFrame(None, -1, "CellProfiler")

        self.frame.start(self.workspace_path, self.pipeline_path)

        if self.abort_initialization:
            return 0

        sys.excepthook = self.__excepthook__

        self.SetTopWindow(self.frame)

        self.frame.Show()

        if self.frame.startup_blurb_frame.IsShownOnScreen():
            self.frame.startup_blurb_frame.Raise()

        return 1

    def OnExit(self):
        import imagej.imagej2

        imagej.imagej2.allow_quit()
