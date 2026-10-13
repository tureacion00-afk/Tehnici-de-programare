from checker import (
    SITES, build_url, is_https, show_response,
    check_site, scan_sites, check_headers, retry_check,
)


def main():
    print("=== Partea 1: build_url și is_https ===")
    print(build_url("example.com", "login"))
    print(build_url("example.com", "/login"))
    print(build_url("https://example.com/", "dashboard"))
    print(is_https("https://example.com"))
    print(is_https("http://example.com"))
    print()

    print("=== Partea 2: show_response ===")
    show_response(SITES[0])
    print()

    print("=== Partea 3: check_site ===")
    for url in SITES:
        print(url, "->", check_site(url))
    print()

    print("=== Partea 4: scan_sites ===")
    scan_sites()
    print()

    print("=== Partea 5: check_headers ===")
    for idx in (10, 11, 0, 9):
        print(SITES[idx])
        print("  ", check_headers(SITES[idx]))
    print()

    print("=== Partea 6: retry_check ===")
    print("200:", retry_check(SITES[3]))
    print("404:", retry_check(SITES[6]))
    print("500:", retry_check(SITES[7]))
    print("500 attempts=2:", retry_check(SITES[7], attempts=2))
    print("invalid:", retry_check(SITES[9]))
    print("random:", retry_check(SITES[12], attempts=5))


if __name__ == "__main__":
    main()