import json
from pathlib import Path

from ticket_triage import get_ticket_by_id
from account_health import load_data, get_account_tickets


# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EVALUATION_DIR = PROJECT_ROOT / "evaluation_results"
EVALUATION_DIR.mkdir(exist_ok=True)

REPORT_FILE = EVALUATION_DIR / "eval_report.json"


# ============================================================
# Helpers
# ============================================================

def print_result(test_id, name, passed, score, details=""):

    status = "PASS" if passed else "FAIL"

    print(
        f"[{status}] {test_id} - {name} | "
        f"Score: {score:.2f}"
    )

    if details:
        print(f"       {details}")


def save_report(report):

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# TASK 1 — Ticket Triage
#
# These tests evaluate deterministic properties of the
# ticket dataset and triage inputs.
#
# They DO NOT call Gemini.
# ============================================================

def evaluate_task1():

    print("\n")
    print("=" * 80)
    print("TASK 1 — INTELLIGENT TICKET TRIAGE")
    print("=" * 80)

    ticket_ids = [
        "TKT-10078",
        "TKT-10112",
        "TKT-10001",
        "TKT-10002"
    ]

    tests = []

    # --------------------------------------------------------
    # Test 1
    # --------------------------------------------------------

    try:

        ticket = get_ticket_by_id("TKT-10078")

        checks = [
            bool(ticket.get("ticket_id")),
            bool(ticket.get("subject")),
            bool(ticket.get("body")),
            bool(ticket.get("product"))
        ]

        score = sum(checks) / len(checks)
        passed = score >= 0.80

        print_result(
            "T1-01",
            "Performance ticket input validation",
            passed,
            score,
            f"Ticket={ticket.get('ticket_id')}"
        )

        tests.append({
            "test_id": "T1-01",
            "test_name": "Performance ticket input validation",
            "passed": passed,
            "quality_score": round(score, 2),
            "details": "Required ticket fields present."
        })

    except Exception as e:

        print_result(
            "T1-01",
            "Performance ticket input validation",
            False,
            0.0,
            str(e)
        )

        tests.append({
            "test_id": "T1-01",
            "test_name": "Performance ticket input validation",
            "passed": False,
            "quality_score": 0.0,
            "details": str(e)
        })

    # --------------------------------------------------------
    # Test 2
    # --------------------------------------------------------

    try:

        ticket = get_ticket_by_id("TKT-10112")

        checks = [
            bool(ticket.get("ticket_id")),
            bool(ticket.get("subject")),
            bool(ticket.get("body")),
            ticket.get("urgency") in ["P1", "P2", "P3", "P4"]
        ]

        score = sum(checks) / len(checks)
        passed = score >= 0.80

        print_result(
            "T1-02",
            "Critical ticket validation",
            passed,
            score,
            f"Urgency in source={ticket.get('urgency')}"
        )

        tests.append({
            "test_id": "T1-02",
            "test_name": "Critical ticket validation",
            "passed": passed,
            "quality_score": round(score, 2),
            "details": "Critical ticket contains valid triage fields."
        })

    except Exception as e:

        print_result(
            "T1-02",
            "Critical ticket validation",
            False,
            0.0,
            str(e)
        )

        tests.append({
            "test_id": "T1-02",
            "test_name": "Critical ticket validation",
            "passed": False,
            "quality_score": 0.0,
            "details": str(e)
        })

    # --------------------------------------------------------
    # Test 3
    # --------------------------------------------------------

    try:

        ticket = get_ticket_by_id("TKT-10001")

        checks = [
            bool(ticket.get("ticket_id")),
            bool(ticket.get("subject")),
            bool(ticket.get("body")),
            ticket.get("account_id") is not None
        ]

        score = sum(checks) / len(checks)
        passed = score >= 0.80

        print_result(
            "T1-03",
            "General support ticket validation",
            passed,
            score,
            f"Account={ticket.get('account_id')}"
        )

        tests.append({
            "test_id": "T1-03",
            "test_name": "General support ticket validation",
            "passed": passed,
            "quality_score": round(score, 2),
            "details": "General support ticket structure is valid."
        })

    except Exception as e:

        print_result(
            "T1-03",
            "General support ticket validation",
            False,
            0.0,
            str(e)
        )

        tests.append({
            "test_id": "T1-03",
            "test_name": "General support ticket validation",
            "passed": False,
            "quality_score": 0.0,
            "details": str(e)
        })

    # --------------------------------------------------------
    # Test 4
    # --------------------------------------------------------

    try:

        ticket = get_ticket_by_id("TKT-10002")

        checks = [
            bool(ticket.get("ticket_id")),
            bool(ticket.get("subject")),
            bool(ticket.get("body")),
            ticket.get("category") is not None
        ]

        score = sum(checks) / len(checks)
        passed = score >= 0.80

        print_result(
            "T1-04",
            "Additional ticket validation",
            passed,
            score,
            f"Category={ticket.get('category')}"
        )

        tests.append({
            "test_id": "T1-04",
            "test_name": "Additional ticket validation",
            "passed": passed,
            "quality_score": round(score, 2),
            "details": "Ticket contains required classification information."
        })

    except Exception as e:

        print_result(
            "T1-04",
            "Additional ticket validation",
            False,
            0.0,
            str(e)
        )

        tests.append({
            "test_id": "T1-04",
            "test_name": "Additional ticket validation",
            "passed": False,
            "quality_score": 0.0,
            "details": str(e)
        })

    # --------------------------------------------------------
    # Test 5 — ADVERSARIAL
    # --------------------------------------------------------

    try:

        from ticket_triage import triage_ticket

        try:

            triage_ticket({})

            # If no exception, invalid input was accepted.
            passed = False
            score = 0.0

            details = (
                "Invalid empty ticket was accepted."
            )

        except ValueError:

            passed = True
            score = 1.0

            details = (
                "Invalid empty ticket correctly rejected."
            )

        print_result(
            "T1-05",
            "Adversarial incomplete ticket",
            passed,
            score,
            details
        )

        tests.append({
            "test_id": "T1-05",
            "test_name": "Adversarial incomplete ticket",
            "adversarial": True,
            "passed": passed,
            "quality_score": score,
            "details": details
        })

    except Exception as e:

        print_result(
            "T1-05",
            "Adversarial incomplete ticket",
            False,
            0.0,
            str(e)
        )

        tests.append({
            "test_id": "T1-05",
            "test_name": "Adversarial incomplete ticket",
            "adversarial": True,
            "passed": False,
            "quality_score": 0.0,
            "details": str(e)
        })

    passed_count = sum(
        1 for test in tests
        if test["passed"]
    )

    average_score = sum(
        test["quality_score"]
        for test in tests
    ) / len(tests)

    print("\n" + "=" * 80)
    print("TASK 1 SUMMARY")
    print("=" * 80)

    print(
        f"Passed: {passed_count}/{len(tests)}"
    )

    print(
        f"Average quality score: {average_score:.2f}"
    )

    return {
        "task": "Task 1 - Intelligent Ticket Triage",
        "passed": passed_count,
        "total": len(tests),
        "average_quality_score": round(
            average_score,
            2
        ),
        "tests": tests
    }


# ============================================================
# TASK 2 — Account Health
#
# These tests validate account/ticket data and the deterministic
# 90-day history logic WITHOUT calling Gemini.
# ============================================================

def evaluate_task2():

    print("\n")
    print("=" * 80)
    print("TASK 2 — TAM ACCOUNT HEALTH")
    print("=" * 80)

    accounts, tickets = load_data()

    account_ids = [
        "ACC-1785",
        "ACC-3336",
        "ACC-5748",
        "ACC-7397"
    ]

    tests = []

    # --------------------------------------------------------
    # Four real accounts
    # --------------------------------------------------------

    for index, account_id in enumerate(
        account_ids,
        start=1
    ):

        test_id = f"T2-0{index}"

        try:

            account = next(
                (
                    a for a in accounts
                    if a.get("account_id") == account_id
                ),
                None
            )

            recent_tickets, reference_date = (
                get_account_tickets(
                    account_id,
                    tickets,
                    days=90
                )
            )

            checks = [
                account is not None,
                bool(account_id),
                reference_date is not None,
                isinstance(recent_tickets, list),
                all(
                    t.get("account_id") == account_id
                    for t in recent_tickets
                )
            ]

            score = sum(checks) / len(checks)

            passed = score >= 0.80

            details = (
                f"90-day tickets={len(recent_tickets)}, "
                f"reference={reference_date.date()}"
            )

            print_result(
                test_id,
                f"Account {account_id} data validation",
                passed,
                score,
                details
            )

            tests.append({
                "test_id": test_id,
                "test_name": f"Account {account_id} data validation",
                "account_id": account_id,
                "passed": passed,
                "quality_score": round(score, 2),
                "details": details
            })

        except Exception as e:

            print_result(
                test_id,
                f"Account {account_id} data validation",
                False,
                0.0,
                str(e)
            )

            tests.append({
                "test_id": test_id,
                "test_name": f"Account {account_id} data validation",
                "account_id": account_id,
                "passed": False,
                "quality_score": 0.0,
                "details": str(e)
            })

    # --------------------------------------------------------
    # Test 5 — ADVERSARIAL
    # --------------------------------------------------------

    try:

        invalid_account = "ACC-INVALID-9999"

        try:

            from account_health import (
                get_account_by_id
            )

            get_account_by_id(
                invalid_account,
                accounts
            )

            passed = False
            score = 0.0

            details = (
                "Invalid account was accepted."
            )

        except ValueError:

            passed = True
            score = 1.0

            details = (
                "Invalid account correctly rejected."
            )

        print_result(
            "T2-05",
            "Adversarial invalid account",
            passed,
            score,
            details
        )

        tests.append({
            "test_id": "T2-05",
            "test_name": "Adversarial invalid account",
            "adversarial": True,
            "passed": passed,
            "quality_score": score,
            "details": details
        })

    except Exception as e:

        print_result(
            "T2-05",
            "Adversarial invalid account",
            False,
            0.0,
            str(e)
        )

        tests.append({
            "test_id": "T2-05",
            "test_name": "Adversarial invalid account",
            "adversarial": True,
            "passed": False,
            "quality_score": 0.0,
            "details": str(e)
        })

    passed_count = sum(
        1 for test in tests
        if test["passed"]
    )

    average_score = sum(
        test["quality_score"]
        for test in tests
    ) / len(tests)

    print("\n" + "=" * 80)
    print("TASK 2 SUMMARY")
    print("=" * 80)

    print(
        f"Passed: {passed_count}/{len(tests)}"
    )

    print(
        f"Average quality score: {average_score:.2f}"
    )

    return {
        "task": "Task 2 - TAM Account Health",
        "passed": passed_count,
        "total": len(tests),
        "average_quality_score": round(
            average_score,
            2
        ),
        "tests": tests
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("#" * 80)
    print("# ZYCUS AI SUPPORT SYSTEM")
    print("# EVALUATION HARNESS")
    print("#" * 80)

    print(
        "\nNOTE: This evaluation harness uses deterministic "
        "dataset/logic checks and does NOT call Gemini."
    )

    # --------------------------------------------------------
    # Task 1
    # --------------------------------------------------------

    task1 = evaluate_task1()

    # --------------------------------------------------------
    # Task 2
    # --------------------------------------------------------

    task2 = evaluate_task2()

    # --------------------------------------------------------
    # Overall statistics
    # --------------------------------------------------------

    total_tests = (
        task1["total"]
        + task2["total"]
    )

    total_passed = (
        task1["passed"]
        + task2["passed"]
    )

    total_failed = (
        total_tests
        - total_passed
    )

    overall_score = (
        total_passed / total_tests
    )

    # --------------------------------------------------------
    # Final report
    # --------------------------------------------------------

    report = {

        "project": "Zycus AI Support System",

        "evaluation_summary": {

            "total_tests": total_tests,

            "total_passed": total_passed,

            "total_failed": total_failed,

            "overall_pass_rate": round(
                overall_score,
                2
            )
        },

        "task_1": task1,

        "task_2": task2
    }

    save_report(report)

    # --------------------------------------------------------
    # Display final result
    # --------------------------------------------------------

    print("\n")
    print("#" * 80)
    print("# FINAL EVALUATION REPORT")
    print("#" * 80)

    print(
        f"Total tests: {total_tests}"
    )

    print(
        f"Passed: {total_passed}"
    )

    print(
        f"Failed: {total_failed}"
    )

    print(
        f"Overall pass rate: "
        f"{overall_score:.2f}"
    )

    print(
        f"\nReport saved to:"
    )

    print(
        REPORT_FILE
    )

    if total_passed == total_tests:

        print(
            "\nSTATUS: ALL TESTS PASSED"
        )

    else:

        print(
            "\nSTATUS: SOME TESTS FAILED"
        )