# -*- coding: utf-8 -*-

from __future__ import print_function

import collections
import json
import os

import pytest

import curlrc


EXAMPLE_CONFIG = '''# output timing data
-s
-S
-o = /dev/null
-w = "url_effective: %{url_effective}\ntime_namelookup: %{time_namelookup}\ntime_connect: %{time_connect}\ntime_appconnect: %{time_appconnect}\ntime_pretransfer: %{time_pretransfer}\ntime_redirect: %{time_redirect}\ntime_starttransfer: %{time_starttransfer}\ntime_total: %{time_total}\n"
'''


@pytest.fixture(params=[
    ('url "curl.haxx.se"', ['url', '"curl.haxx.se"']),
    ('url = "curl.haxx.se"', ['url', '"curl.haxx.se"']),
    ('url="curl.haxx.se"', ['url', '"curl.haxx.se"']),
    ('url ="curl.haxx.se"', ['url', '"curl.haxx.se"']),
    ('url:"curl.haxx.se"', ['url', '"curl.haxx.se"']),
    ('url : "curl.haxx.se"', ['url', '"curl.haxx.se"']),
    ('url: "curl.haxx.se"', ['url', '"curl.haxx.se"']),
    ('url :"curl.haxx.se"', ['url', '"curl.haxx.se"']),
    ('-O', ['-O', True]),
])
def test_data(request):
    return request.param


@pytest.fixture
def test_config(tmpdir):
    p = tmpdir.join('time.rc')
    p.write(EXAMPLE_CONFIG)
    assert p.read() == EXAMPLE_CONFIG
    return p


@pytest.fixture
def test_template():
    return 'url_effective: %{url_effective}\ntime_namelookup: %{time_namelookup}\ntime_connect: %{time_connect}'


@pytest.fixture
def test_template_map():
    template_map = collections.OrderedDict()
    template_map['url_effective'] = '%{url_effective}'
    template_map['time_namelookup'] = '%{time_namelookup}'
    template_map['time_connect'] = '%{time_connect}'
    return template_map


@pytest.fixture(params=[
    (True, 'url_effective,time_namelookup,time_connect\n%{url_effective},%{time_namelookup},%{time_connect}\n'),
    (False, '%{url_effective},%{time_namelookup},%{time_connect}\n'),
])
def test_template_as_csv(request):
    return request.param


@pytest.fixture(params=[
    (True, '''url_effective	%{url_effective}
time_namelookup	%{time_namelookup}
time_connect	%{time_connect}
'''),
    (False, '''%{url_effective}
%{time_namelookup}
%{time_connect}
'''),
])
def test_template_as_table(request):
    return request.param


@pytest.fixture(params=[
    (True, json.dumps(test_template_map(), indent=2) + '\n'),
    (False, json.dumps(test_template_map()) + '\n'),
])
def test_template_as_json(request):
    return request.param


class TestCurlConfig:
    def test_split_lines(self, test_data):
        (input, expected) = test_data
        assert curlrc.CurlConfig.split_line(input) == expected

    def test_from_file(self, test_config):
        config = curlrc.CurlConfig.from_file(str(test_config))
        assert config.name == 'time'
        assert config.description == 'output timing data'
        assert config.path == str(test_config)
        assert config.template


class TestCurlTemplate:
    def test_from_str(self, test_template, test_template_map):
        tmpl = curlrc.CurlTemplate.from_str(test_template)
        assert tmpl._map == test_template_map

    def test_as_csv(self, test_template, test_template_as_csv):
        tmpl = curlrc.CurlTemplate.from_str(test_template)
        (input, expected) = test_template_as_csv
        assert tmpl.as_csv(input) == expected

    def test_as_table(self, test_template, test_template_as_table):
        tmpl = curlrc.CurlTemplate.from_str(test_template)
        (input, expected) = test_template_as_table
        assert tmpl.as_table(input) == expected

    def test_as_json(self, test_template, test_template_as_json):
        tmpl = curlrc.CurlTemplate.from_str(test_template)
        (input, expected) = test_template_as_json
        assert tmpl.as_json(input) == expected


def test_curl_configs(tmpdir):
    files = [
        'example1.rc',
        'example2.rc',
        'example3'
    ]
    for f in files:
        p = tmpdir.join(f)
        p.write('')
    glob = [
        str(tmpdir.join('example1.rc')),
        str(tmpdir.join('example2.rc')),
    ]
    assert curlrc.curl_configs(str(tmpdir)) == glob
