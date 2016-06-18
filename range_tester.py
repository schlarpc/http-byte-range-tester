import requests
import inspect
import sys
import inspect
import traceback

OK = 200
PARTIAL_CONTENT = 206
RANGE_NOT_SATISFIABLE = 416

tests = {
    'baseline': {},
    'zero_to_eof': {'Range': 'bytes=0-'},
    'first_byte': {'Range': 'bytes=0-0'},
    'last_five_hundred': {'Range': 'bytes=-500'},
    'big_from_front': {'Range': 'bytes=0-9999999999'},
    'big_from_back': {'Range': 'bytes=-9999999999'},
    'out_of_bounds': {'Range': 'bytes=99999999999-9999999999999999'},
    'multiple': {'Range': 'bytes=0-100,200-300'},
    'other_unit': {'Range': 'breads=0-5'},
    'overlapping': {'Range': 'bytes=0-100,50-150'},
    'edging': {'Range': 'bytes=0-100,101-150'},
    'nonnumeric': {'Range': 'bytes=chex-mix'},
    'empty': {'Range': 'bytes='},
    'unbound': {'Range': 'bytes=-'},
    'higher_first': {'Range': 'bytes=200-50'},
}

results = {}

def accepts_ranges():
    assert results['baseline'].headers.get('Accept-Ranges') == 'bytes'

def first_byte_content():
    assert bytes([results['baseline'].content[0]]) == results['first_byte'].content

def first_byte_headers():
    expected = 'bytes 0-0/{}'.format(len(results['baseline'].content))
    assert results['first_byte'].headers.get('Content-Range', '') == expected

def first_byte_status():
    assert results['first_byte'].status_code == PARTIAL_CONTENT

def zero_to_eof_content():
    assert results['baseline'].content == results['zero_to_eof'].content

def zero_to_eof_headers():
    expected = 'bytes 0-{}/{}'.format(
        len(results['baseline'].content) - 1,
        len(results['baseline'].content))
    assert results['zero_to_eof'].headers.get('Content-Range', '') == expected

def zero_to_eof_status():
    assert results['zero_to_eof'].status_code == PARTIAL_CONTENT

def last_five_hundred_content():
    assert results['baseline'].content[-500:] == results['last_five_hundred'].content

def last_five_hundred_headers():
    expected = 'bytes {}-{}/{}'.format(
        len(results['baseline'].content) - 500,
        len(results['baseline'].content) - 1,
        len(results['baseline'].content))
    assert results['last_five_hundred'].headers.get('Content-Range', '') == expected

def multiple_content_type():
    assert results['multiple'].headers.get('Content-Type', '').split(';')[0] == 'multipart/byteranges'

def multiple_status():
    assert results['multiple'].status_code == PARTIAL_CONTENT

def big_from_front_content():
    assert results['baseline'].content == results['big_from_front'].content

def big_from_front_status():
    assert results['big_from_front'].status_code == PARTIAL_CONTENT

def big_from_back_content():
    assert results['baseline'].content == results['big_from_back'].content

def big_from_back_status():
    assert results['big_from_back'].status_code == PARTIAL_CONTENT

def overlapping_content_type():
    assert results['overlapping'].headers.get('Content-Type', '').split(';')[0] != 'multipart/byteranges'

def overlapping_status():
    assert results['overlapping'].status_code in (OK, PARTIAL_CONTENT)

def edging_content_type():
    assert results['edging'].headers.get('Content-Type', '').split(';')[0] != 'multipart/byteranges'

def edging_status():
    assert results['edging'].status_code in (OK, PARTIAL_CONTENT)

def other_unit_status():
    assert results['other_unit'].status_code in (OK, RANGE_NOT_SATISFIABLE)

def nonnumeric_status():
    assert results['nonnumeric'].status_code in (OK, RANGE_NOT_SATISFIABLE)

def unbound_status():
    assert results['unbound'].status_code in (OK, RANGE_NOT_SATISFIABLE)

def last_five_hundred_status():
    assert results['last_five_hundred'].status_code == PARTIAL_CONTENT

def out_of_bounds_status():
    assert results['out_of_bounds'].status_code in (OK, RANGE_NOT_SATISFIABLE)

def out_of_bounds_header():
    if results['out_of_bounds'].status_code == RANGE_NOT_SATISFIABLE:
        expected = 'bytes */{}'.format(len(results['baseline'].content))
        assert results['out_of_bounds'].headers.get('Content-Range', '') == expected

def higher_first_status():
    assert results['higher_first'].status_code in (OK, RANGE_NOT_SATISFIABLE)

def higher_first_header():
    if results['higher_first'].status_code == RANGE_NOT_SATISFIABLE:
        expected = 'bytes */{}'.format(len(results['baseline'].content))
        assert results['higher_first'].headers.get('Content-Range', '') == expected


if __name__ == '__main__':
    if not len(sys.argv):
        print('Usage: range_tester.py <url>')
        sys.exit(1)
    url = sys.argv[1]

    results = {description: requests.get(url, headers=headers) for description, headers in tests.items()}
    funcs = [x for x in inspect.getmembers(sys.modules[__name__]) if inspect.isfunction(x[1])]
    funcs.sort()
    for name, obj in funcs:
        print(name.ljust(40), end='')
        try:
            obj()
        except Exception:
            print('FAIL')
        else:
            print('OK')


