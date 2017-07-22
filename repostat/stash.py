import redis
import subprocess
import time
import copy
import pickle


class StatStash:
    def __init__(self, redis_url):
        self.r = redis.Redis.from_url(redis_url)
        self.r.ping()
        self.current_branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode(
            "utf-8").strip()
        self.local_head = subprocess.check_output(
            ['git', 'log', '-n', '1', '--pretty=format:%H']).decode("utf-8")

    def report_stats(self, stat_type, stats, overwrite=True):
        """
        Store the statistics in redis, indexed by commit. 
        :param stat_type: a key for the stat group
        :type stat_type: str
        :param stats: the statistics to store
        :type stats: dict
        :return: 
        :rtype: 
        """
        if stat_type == "branch":
            raise ValueError('error type cannot be named "branch"')
        if not overwrite and self.r.hexists(stat_type, self.local_head):
            raise ValueError("Commit has already be recorded")
        stat_rep = copy.copy(stats)
        stat_rep['commit'] = self.local_head
        stat_rep['branch'] = self.current_branch
        stat_rep['timestamp'] = time.time()
        self.r.zadd("branch:" + stat_rep['branch'], stat_rep['commit'],
               stat_rep['timestamp'], )
        self.r.hset(stat_type, stat_rep['commit'], pickle.dumps(stat_rep))

    def get_current_stats(self, stat_type, branch="master"):
        """
        Pull the latest stats of a given type for a given branch
        :param stat_type: a key for the stat group
        :type stat_type: str
        :param branch: the branch for the stats
        :type branch: str
        :return: a stat group
        :rtype: dict
        """
        commit = self.r.zrange("branch:"+branch, -2, -1)[0]
        hit = self.r.hget(stat_type, commit)
        if not hit:
            raise ValueError('No data for master branch found')
        return pickle.loads(hit)

    def get_difference(self, stat_type, stats, branch='master', ignore=('commit', 'branch', 'timestamp')):
        """
        Return a stats object with the difference between the provided stats 
        and the the current set of stats on the branch
        :param stat_type: a key for the stat group
        :type stat_type: str
        :param stats: a stats group
        :type stats: dict
        :param branch: the branch to compare with
        :type branch: str
        :param ignore: keys in the stats group to ignore
        :type ignore: tuple
        :return: stats
        :rtype: dict
        """
        basis_stats = self.get_current_stats(stat_type, branch)
        diff = {}
        for key, val in stats.items():
            if key in ignore:
                continue
            if isinstance(val, str):
                print("WARNING: method does not calculate difference for "
                      "strings. consider using 'get_new' method")
                continue
            if isinstance(val, float) or isinstance(val, int):
                diff[key] = val - basis_stats.get(key, 0)
            else:
                diff[key] = len(val) - len(basis_stats.get(key, ''))
        return diff

    def get_decreasing(self, stat_type, stats, branch='master',
                       ignore=('commit', 'branch', 'timestamp')):
        """
        Get the keys for stats values which decrease in a given set as compared
         with the current stats on a branch
        :param stat_type: a key for the stat group
        :type stat_type: str
        :param stats: a stats group
        :type stats: dict
        :param branch: the branch to compare with
        :type branch: str
        :param ignore: keys in the stats group to ignore
        :type ignore: tuple
        :return: keys of stats that decreased
        :rtype: list
        """
        difference = self.get_difference(stat_type, stats, branch, ignore)
        return [k for k, v in difference.items() if v < 0]

    def get_increasing(self, stat_type, stats, branch='master',
                       ignore=('commit', 'branch', 'timestamp')):
        """
        Get the keys for stats values which increase in a given set as compared
         with the current stats on a branch
        :param stat_type: a key for the stat group
        :type stat_type: str
        :param stats: a stats group
        :type stats: dict
        :param branch: the branch to compare with
        :type branch: str
        :param ignore: keys in the stats group to ignore
        :type ignore: tuple
        :return: keys of stats that increased
        :rtype: list
        """
        difference = self.get_difference(stat_type, stats, branch, ignore)
        return [k for k, v in difference.items() if v > 0]

    def get_new(self, stat_type, stats, branch='master', ignore=('commit', 'branch', 'timestamp')):
        """
        Get the keys for stats values which increase in a given set as compared
         with the current stats on a branch
        :param stat_type: a key for the stat group
        :type stat_type: str
        :param stats: a stats group
        :type stats: dict
        :param branch: the branch to compare with
        :type branch: str
        :param ignore: keys in the stats group to ignore
        :type ignore: tuple
        :return: stats that contain new values
        :rtype: dict
        """
        basis_stats = self.get_current_stats(stat_type, branch)
        new = {}
        for key, val in stats.items():
            if key in ignore:
                continue
            if getattr(val, "__iter__", False) and not isinstance(val, str):
                diff = set(val) - set(basis_stats.get(key, []))
                if diff:
                    new[key] = diff
            elif val != basis_stats.get(key, ''):
                new[key] = val
        return new
