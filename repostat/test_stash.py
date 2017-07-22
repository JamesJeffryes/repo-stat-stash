from repostat.stash import StatStash
from nose.tools import assert_raises

stash = StatStash('redis-16221.c12.us-east-1-4.ec2.cloud.redislabs.com', 16221)
stash.current_branch = 'test_branch'
stat_one = {"a":1, "b":2, "c":3}
stat_two = {"a":3, "b":2, "c":1}


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


def test_get_increasing():
    assert stash.get_increasing('test', stat_two) == ['a']
