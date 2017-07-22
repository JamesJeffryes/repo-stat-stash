from repostat.stash import StatStash
from nose.tools import assert_raises

stash = StatStash('redis-16221.c12.us-east-1-4.ec2.cloud.redislabs.com', 16221)
stash.current_branch = 'test_branch'
stat_one = {"a": 1, "b": ('z',), "c": [1, 2, 3], 'd': {}, 'e': {'x', 'y'}}
stat_two = {"a": 3, "b": ('x',), "c": [1], 'd': {}, 'e': {'x', 'z'}}


def teardown_module():
    stash.r.delete("branch:test_branch")
    stash.r.delete("test")


def test_report_stats():
    stash.report_stats('test', stat_one)
    assert stash.r.hget("test", stash.local_head)
    assert_raises(ValueError, stash.report_stats, 'branch', stat_one)
    assert_raises(ValueError, stash.report_stats, 'test', stat_one, False)


def test_get_current_stats():
    result = stash.get_current_stats('test', stash.current_branch)
    assert all([result[k] == stat_one[k] for k in stat_one])


def test_get_difference():
    assert stash.get_difference('test', stat_two, stash.current_branch
                                ) == {'a': 2, 'b': 0, 'c': -2, 'd': 0, 'e': 0}


def test_get_decreasing():
    assert stash.get_decreasing('test', stat_two, stash.current_branch
                                ) == ['c']


def test_get_increasing():
    assert stash.get_increasing('test', stat_two, stash.current_branch
                                ) == ['a']
