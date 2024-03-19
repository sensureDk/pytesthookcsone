from datetime import datetime

import requests
from _pytest.config import Config
from _pytest.main import Session
from _pytest.nodes import Item
from _pytest.reports import TestReport

data = {"failed": 0, "passed": 0, "skipped": 0}


def pytest_configure(config: Config):
    """处理测试开始时相关事宜"""
    data["start_time"] = datetime.now()


def pytest_collection_finish(session: "Session"):
    """用例加载完毕后使用，session提供了所有的"""
    data["total_cases"] = session.items.__len__()
    print(f"收集到的测试用例有{data['total_cases']}个")
    assert data["total_cases"] == 3


def pytest_runtest_call(item: "Item"):
    data[item.nodeid + "start_time"] = datetime.now()
    print(f"案例{item.nodeid}开始执行时间{data[item.nodeid+'start_time']}")


#
def pytest_runtest_logreport(report: "TestReport"):
    """每个测试案例执行完毕时调用"""

    if report.when == "call":
        data[report.nodeid + "end_time"] = datetime.now()
        print(f"案例{report.nodeid}开始执行时间{data[report.nodeid+'end_time']}")
        data[report.nodeid + "case_time"] = (
            data[report.nodeid + "end_time"] - data[report.nodeid + "start_time"]
        )
        if report.outcome == "failed":
            data["failed"] += 1
        elif report.outcome == "passed":
            data["passed"] += 1
        elif report.outcome == "skipped":
            data["skipped"] += 1
        else:
            raise Exception
        print(
            f"案例{report.nodeid}执行时长：{data[report.nodeid+'case_time'].total_seconds()}"
        )


#


def pytest_unconfigure():
    """处理测试完毕后相关事宜"""
    data["end_time"] = datetime.now()
    data["durn_time"] = data["end_time"] - data["start_time"]
    # assert timedelta(seconds=3).total_seconds() > data["durn_time"].total_seconds()>=timedelta(seconds=2.5).total_seconds()
    # assert data["passed"] == 2
    # assert data["failed"] == 1
    # assert data["skipped"] == 0
    data["pass_rate"] = (
        data["passed"] / data["total_cases"] if data["total_cases"] > 0 else 0
    )
    data["fail_rate"] = (
        data["failed"] / data["total_cases"] if data["total_cases"] > 0 else 0
    )
    data["skipp_rate"] = (
        data["skipped"] / data["total_cases"] if data["total_cases"] > 0 else 0
    )
    data["pass_rate"] = "{:.2%}".format(data["pass_rate"])
    data["fail_rate"] = "{:.2%}".format(data["fail_rate"])
    data["skipp_rate"] = "{:.2%}".format(data["skipp_rate"])

    print(f'成功{data["pass_rate"]}\n失败{data["fail_rate"]}\n跳过{data["skipp_rate"]}')

    print(f'执行时长{data["durn_time"]}')

    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=4798277e-32d4-4cc3-8bdb-cadb579d45fc"

    json_data = {
        "msgtype": "markdown",
        "markdown": {
            "content": f"""<font color=\"warning\">测试结果汇报请相关同事注意</font>\n> 测试案例总计:<font color=\"comment\">{data["total_cases"]}</font>\n> 测试通过:<font color=\"blue\">{data["passed"]}</font>\n> 测试失败:<font color=\"red\">{data["failed"]}</font>"""
        },
    }

    req = requests.post(url=url, json=json_data)

    assert req.status_code == 200
