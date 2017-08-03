# repo-stat-stash
This tool to stores custom repository statistics and issues with commit level resolution in a redis store. This solution was inspired by automatic code quality checking services like codacy or codecov, which examine code for coding style violations and evaluate commits on the basis of if they reduce or increase the quality of the codebase.

It grew out of a desire to implement custom data quality checking for a scientific database stored in GitHub. In a lot of ways, GitHub is a great way to store scientific data; it's open, clearly versioned and supports collaborative curation and automatic error checking. However, while custom quality checks on each commit are simple to implement with a CI server like Travis, they fail to account for accumulated curation issues (similar to technical debt). Using this module, these tests can compare the issues in commit to the repository head and ensure that revisions improve the consistency and quality of the data.

### Usage
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
You can update your CI tests to only fail if new issues are found quite easily. Make sure you also save results in the test file so the bar gets raised when fixes are pulled into the master branch.
```
> issues = run_your_test_library()
> new_issues = stash.get_new('example errors', issues)
> stash.report_stats('example errors', issues) # make sure the record is updated regardless
> if new_issues:
    print("New issues detected: %s" % new_issues)
    exit(1) # causes travis build to fail
``` 
