# repo-stat-stash
This tool to stores custom repository statistics and issues with commit level resolution in a redis store. This solution was inspired by automatic code quality checking services like codacy or codecov, which examine code for coding style violations and evaluate commits on the basis of weather they reduce or increase the quality of the codebase.

It grew out of a desire to implement custom data quality checking for a scientific database stored in GitHub. Custom quality checks on each commit are simple to implement with a CI server like Travis but fail to account for accumulated technical debt. Using this module, these tests can compare the issues in commit to the repository head and ensure that revisions improve the consistency and quality of the data.

###Usage
This tool needs a redis store to persist it's data. You can set up a free redis instance in the cloud to test this tool out from [redislabs](https://redislabs.com/blog/redis-cloud-30mb-ram-30-connections-for-free/). With that endpoint in hand, initialize the StatStash as follows:
```
> from repostat.stash import StatStash
> stash = StatStash('redis://redistogo:97514a86e6ef0787d7c13696ca95db1d@angelfish.redistogo.com:10495')
```
Save data to the redis store as follows. The stat_type must be a string (ex. 'example errors') while the statistics should be a dictionary.
```
> stat_one = {"faulty formulas": 1, "duplicate name": ('glucose',), "blank lines": [1, 2, 3], 'missing data': {'x', 'y'}}
> stash.report_stats('example errors', stat_one)
```
Check how a new set of stats compares with the stats recorded for the master branch. You can look how the counts change as a whole of focus on only new, decreasing or increasing data_types.
```
> stat_two = {"faulty formulas": 3, "duplicate name": ('glucose',), "blank lines": [1], 'd': "", 'missing data': {'x', 'z'}}
> print(stash.get_difference('example errors', stat_two))
{'duplicate name': 0, 'blank lines': -2, 'faulty formulas': 2, 'missing data': 0}
> print(stash.get_increasing('example errors', stat_two))
['faulty formulas']
> print(stash.get_new('example errors', stat_two))
{'faulty formulas': 3, 'missing data': {'z'}}
```
