import sys
from missions import (
    getMissionCountByCompany,
    getSuccessRate,
    getMissionsByDateRange,
    getTopCompaniesByMissionCount,
    getMissionStatusCount,
    getMissionsByYear,
    getMostUsedRocket,
    getAverageMissionsPerYear,
)

PASS = 0
FAIL = 0


def check(label, condition):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✓ {label}")
    else:
        FAIL += 1
        print(f"  ✗ FAIL — {label}")


def raises(exc_type, func, *args, **kwargs):
    try:
        func(*args, **kwargs)
        return False
    except exc_type:
        return True
    except Exception:
        return False


def test_getMissionCountByCompany():
    print("\n1. getMissionCountByCompany")
    r = getMissionCountByCompany("SpaceX")
    check("SpaceX has missions", r > 0)
    check("Returns int", isinstance(r, int))
    check("Unknown company → 0", getMissionCountByCompany("FakeCompany123") == 0)
    check("Empty string → 0",    getMissionCountByCompany("") == 0)
    check("Whitespace string → 0", getMissionCountByCompany("   ") == 0)
    check("None → TypeError",   raises(TypeError, getMissionCountByCompany, None))
    check("int → TypeError",    raises(TypeError, getMissionCountByCompany, 123))
    check("float → TypeError",  raises(TypeError, getMissionCountByCompany, 3.14))
    check("list → TypeError",   raises(TypeError, getMissionCountByCompany, ["NASA"]))
    check("dict → TypeError",   raises(TypeError, getMissionCountByCompany, {}))
    check("bool → TypeError",   raises(TypeError, getMissionCountByCompany, True))


def test_getSuccessRate():
    print("\n2. getSuccessRate")
    r = getSuccessRate("SpaceX")
    check("SpaceX rate 0–100",   0 <= r <= 100)
    check("Returns float",       isinstance(r, float))
    check("Max 2 decimal places", round(r, 2) == r)
    check("Unknown company → 0.0", getSuccessRate("FakeCompany123") == 0.0)
    check("Empty string → 0.0",    getSuccessRate("") == 0.0)
    check("None → TypeError",  raises(TypeError, getSuccessRate, None))
    check("int → TypeError",   raises(TypeError, getSuccessRate, 42))
    check("float → TypeError", raises(TypeError, getSuccessRate, 3.14))
    check("list → TypeError",  raises(TypeError, getSuccessRate, []))
    check("bool → TypeError",  raises(TypeError, getSuccessRate, False))


def test_getMissionsByDateRange():
    print("\n3. getMissionsByDateRange")
    r = getMissionsByDateRange("2020-01-01", "2020-12-31")
    check("2020 returns list",   isinstance(r, list))
    check("2020 has missions",   len(r) > 0)
    r1957 = getMissionsByDateRange("1957-01-01", "1957-12-31")
    check("1957 first = Sputnik-1", r1957 and r1957[0] == "Sputnik-1")
    check("Same start=end works",   isinstance(getMissionsByDateRange("2020-06-01", "2020-06-01"), list))
    check("No missions range → []", getMissionsByDateRange("1900-01-01", "1900-12-31") == [])
    check("start > end → ValueError",
          raises(ValueError, getMissionsByDateRange, "2020-12-31", "2020-01-01"))
    check("Bad format → ValueError",
          raises(ValueError, getMissionsByDateRange, "not-a-date", "2020-12-31"))
    check("Empty startDate → ValueError",
          raises(ValueError, getMissionsByDateRange, "", "2020-12-31"))
    check("Empty endDate → ValueError",
          raises(ValueError, getMissionsByDateRange, "2020-01-01", ""))
    check("Partial '2020' → ValueError",
          raises(ValueError, getMissionsByDateRange, "2020", "2020-12-31"))
    check("Ambiguous '01-02-03' → ValueError",
          raises(ValueError, getMissionsByDateRange, "01-02-03", "2020-12-31"))
    check("Slash format '01/01/2020' → ValueError",
          raises(ValueError, getMissionsByDateRange, "01/01/2020", "2020-12-31"))
    check("TZ-aware 'Z' suffix → ValueError",
          raises(ValueError, getMissionsByDateRange, "2020-01-01Z", "2020-12-31"))
    check("TZ offset '+05:30' → ValueError",
          raises(ValueError, getMissionsByDateRange, "2020-01-01T00:00:00+05:30", "2020-12-31"))
    check("None startDate → TypeError",
          raises(TypeError, getMissionsByDateRange, None, "2020-12-31"))
    check("None endDate → TypeError",
          raises(TypeError, getMissionsByDateRange, "2020-01-01", None))
    check("int startDate → TypeError",
          raises(TypeError, getMissionsByDateRange, 20200101, "2020-12-31"))
    check("list → TypeError",
          raises(TypeError, getMissionsByDateRange, ["2020-01-01"], "2020-12-31"))


def test_getTopCompaniesByMissionCount():
    print("\n4. getTopCompaniesByMissionCount")
    r = getTopCompaniesByMissionCount(5)
    check("Returns list",         isinstance(r, list))
    check("Length == 5",          len(r) == 5)
    check("Items are 2-tuples",   all(isinstance(x, tuple) and len(x) == 2 for x in r))
    check("Counts descending",    all(r[i][1] >= r[i+1][1] for i in range(len(r)-1)))
    check("n=0 → []",             getTopCompaniesByMissionCount(0) == [])
    check("n > companies → all",  len(getTopCompaniesByMissionCount(9999)) > 0)
    check("None → TypeError",      raises(TypeError, getTopCompaniesByMissionCount, None))
    check("str '5' → TypeError",   raises(TypeError, getTopCompaniesByMissionCount, "5"))
    check("float 5.0 → TypeError", raises(TypeError, getTopCompaniesByMissionCount, 5.0))
    check("bool True → TypeError", raises(TypeError, getTopCompaniesByMissionCount, True))
    check("list → TypeError",      raises(TypeError, getTopCompaniesByMissionCount, [5]))
    check("n=-1 → ValueError",     raises(ValueError, getTopCompaniesByMissionCount, -1))
    check("n=-100 → ValueError",   raises(ValueError, getTopCompaniesByMissionCount, -100))


def test_getMissionStatusCount():
    print("\n5. getMissionStatusCount")
    r = getMissionStatusCount()
    check("Returns dict",                isinstance(r, dict))
    check("Has 'Success'",               "Success" in r)
    check("Has 'Failure'",               "Failure" in r)
    check("Has 'Partial Failure'",       "Partial Failure" in r)
    check("Has 'Prelaunch Failure'",     "Prelaunch Failure" in r)
    check("All values are ints",         all(isinstance(v, int) for v in r.values()))
    check("Total missions > 0",          sum(r.values()) > 0)


def test_getMissionsByYear():
    print("\n6. getMissionsByYear")
    check("2020 has missions",         getMissionsByYear(2020) > 0)
    check("Returns int",               isinstance(getMissionsByYear(2020), int))
    check("1957 has missions",         getMissionsByYear(1957) > 0)
    check("1900 → 0",                  getMissionsByYear(1900) == 0)
    check("Far future → 0",            getMissionsByYear(3000) == 0)
    check("None → TypeError",          raises(TypeError, getMissionsByYear, None))
    check("str '2020' → TypeError",    raises(TypeError, getMissionsByYear, "2020"))
    check("float 2020.0 → TypeError",  raises(TypeError, getMissionsByYear, 2020.0))
    check("bool True → TypeError",     raises(TypeError, getMissionsByYear, True))
    check("list → TypeError",          raises(TypeError, getMissionsByYear, [2020]))
    check("year=0 → ValueError",       raises(ValueError, getMissionsByYear, 0))
    check("year=-1 → ValueError",      raises(ValueError, getMissionsByYear, -1))
    check("year=-2020 → ValueError",   raises(ValueError, getMissionsByYear, -2020))
    check("year=10000 → ValueError",   raises(ValueError, getMissionsByYear, 10000))


def test_getMostUsedRocket():
    print("\n7. getMostUsedRocket")
    r = getMostUsedRocket()
    check("Returns str",     isinstance(r, str))
    check("Non-empty",       len(r) > 0)
    check("Expected rocket", r == "Cosmos-3M (11K65M)")


def test_getAverageMissionsPerYear():
    print("\n8. getAverageMissionsPerYear")
    r = getAverageMissionsPerYear(2010, 2020)
    check("Returns float",         isinstance(r, float))
    check("Positive average",      r > 0)
    check("Max 2 decimal places",  round(r, 2) == r)
    single = getAverageMissionsPerYear(2020, 2020)
    check("Single year == getMissionsByYear", single == float(getMissionsByYear(2020)))
    check("Empty range → 0.0",     getAverageMissionsPerYear(1900, 1910) == 0.0)
    check("start > end → ValueError",
          raises(ValueError, getAverageMissionsPerYear, 2020, 2010))
    check("None startYear → TypeError",
          raises(TypeError, getAverageMissionsPerYear, None, 2020))
    check("None endYear → TypeError",
          raises(TypeError, getAverageMissionsPerYear, 2010, None))
    check("str startYear → TypeError",
          raises(TypeError, getAverageMissionsPerYear, "2010", 2020))
    check("float endYear → TypeError",
          raises(TypeError, getAverageMissionsPerYear, 2010, 2020.0))
    check("bool → TypeError",
          raises(TypeError, getAverageMissionsPerYear, True, 2020))
    check("startYear=0 → ValueError",    raises(ValueError, getAverageMissionsPerYear, 0, 2020))
    check("endYear=-1 → ValueError",     raises(ValueError, getAverageMissionsPerYear, 2010, -1))
    check("startYear=10000 → ValueError", raises(ValueError, getAverageMissionsPerYear, 10000, 10001))
    check("endYear=10000 → ValueError",   raises(ValueError, getAverageMissionsPerYear, 2020, 10000))


if __name__ == "__main__":
    print("=" * 70)
    print("SPACE MISSIONS — FUNCTION TESTS (normal + invalid inputs)")
    print("=" * 70)

    test_getMissionCountByCompany()
    test_getSuccessRate()
    test_getMissionsByDateRange()
    test_getTopCompaniesByMissionCount()
    test_getMissionStatusCount()
    test_getMissionsByYear()
    test_getMostUsedRocket()
    test_getAverageMissionsPerYear()

    print("\n" + "=" * 70)
    total = PASS + FAIL
    print(f"Results: {PASS}/{total} passed  |  {FAIL} failed")
    print("✓ ALL TESTS PASSED!" if FAIL == 0 else "✗ Some tests FAILED — see above.")
    print("=" * 70)
    sys.exit(0 if FAIL == 0 else 1)
