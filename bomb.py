def solution(m, f):
    count = 0
    m = int(m)
    f = int(f)
    m, f = max(m, f), min(m, f)
    while f != 1:
        if m % f == 0:
            return "impossible"

        count += m / f
        m, f = f, m % f
    count += m - 1

    return str(count)


assert (solution("2", "1") == "1")
assert (solution("2", "4") == "impossible")
assert (solution("4", "7") == "4")
assert (solution("7", "4") == "4")
assert (solution("100000000000000000000000000000000000000000000000000",
                 "1") == "99999999999999999999999999999999999999999999999999")
assert (solution(12345, 54322) == '150')
print(solution(4, 2 + 4))
