import subprocess
import os


def get_repro_context():
    hg_rev = (
        subprocess.check_output(["hg", "id", "--id"], cwd=os.path.dirname(__file__))
        .strip()
        .decode("ascii")
    )
    hg_diff = subprocess.check_output(
        ["hg", "diff"], cwd=os.path.dirname(__file__)
    ).strip().decode("utf8")
    context = dict(hg_rev=hg_rev, hg_diff=hg_diff)
    return context
