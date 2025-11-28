import subprocess, os


def WritePassword(process: subprocess.Popen, password: str):
    try:
        stdout, stderr = process.communicate(input=password, timeout=10)

        if process.returncode == 0:
            return stdout

        if process.returncode != 0:
            return stderr

    except subprocess.TimeoutExpired:
        return "Non worked process"


def ChangePasswordLinux(
    who_need_rename: str,
    new_password: str,
    launch_password: str = None,
    launch_user: str = None,
):
    try:
        # "/usr/bin/sudo", "-S",
        proc = subprocess.Popen(
            ["passwd", who_need_rename],
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            user=launch_user,
        )

        line_to_write = (
            f"{launch_password+"\n" if launch_password is not None else ""}"
            + f"{new_password}\n" * 2
        )
        x = WritePassword(proc, line_to_write)
        print(x)

        proc.wait(timeout=5)
    except subprocess.TimeoutExpired as ex:
        print(f"Процесс завершен с ошибкой: {ex}")
        proc.kill()

    return


def ChangePasswordWindows(user: str, password: str):
    os.system(f"net user {user} {password}")
