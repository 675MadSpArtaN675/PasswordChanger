import sys

import win32serviceutil as w32su
import win32service as w32s
import servicemanager as sm


from server import ChangerService


class ChangerServiceFramework(w32su.ServiceFramework):
    _svc_name_ = "PasswordChanger"
    _svc_display_name_ = "Password changer for Windows"

    def SvcDoRun(self):
        self.ReportServiceStatus(w32s.SERVICE_START_PENDING)
        self.__changer = ChangerService()
        self.ReportServiceStatus(w32s.SERVICE_RUNNING)

        self.__changer.Launch()

    def SvcStop(self):
        self.ReportServiceStatus(w32s.SERVICE_START_PENDING)
        self.__changer.Stop()
        self.ReportServiceStatus(w32s.SERVICE_STOPPED)


def init_service():
    if len(sys.argv) == 1:
        sm.Initialize()
        sm.PrepareToHostSingle(ChangerServiceFramework)
        sm.StartServiceCtrlDispatcher()

    else:
        w32su.HandleCommandLine(ChangerServiceFramework)


if __name__ == "__main__":
    init_service()
