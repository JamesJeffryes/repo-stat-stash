import redis
import subprocess
import time
import copy
import pickle


class StatStash:
    def __init__(self, *redis_params):
        self.r = redis.Redis(*redis_params)
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
        basis_stats = self.get_current_stats(stat_type, branch)
        inc = []
        for key, val in stats.items():
            if key in ignore:
                continue
            if val > basis_stats[key]:
                inc.append(key)
        return inc

    def get_new(self, stat_type, stats, ignore=('commit', 'branch', 'timestamp')):
        raise NotImplementedError

    def get_difference(self, stat_type, stats, ignore=('commit', 'branch', 'timestamp')):
        raise NotImplementedError
