"""
Plot module for util functionality.
"""

import typing as tp
import functools
from pathlib import Path

import pygit2

from varats.data.reports.commit_report import CommitMap
from varats.utils.project_util import (get_local_project_git,
                                       create_git_project_wrapper)


def __check_required_args_impl(required_args: tp.List[str],
                               kwargs: tp.Dict[str, tp.Any]) -> None:
    """
    Implementation to check if all required graph args are passed by the user.
    """
    for arg in required_args:
        if arg not in kwargs:
            raise AssertionError(
                "Argument {} was not specified but is required for this graph.".
                format(arg))


def check_required_args(
        required_args: tp.List[str]
) -> tp.Callable[[tp.Callable[..., tp.Any]], tp.Callable[..., tp.Any]]:
    """
    Check if all required graph args are passed by the user.
    """

    def decorator_pp(func: tp.Callable[..., tp.Any]
                    ) -> tp.Callable[..., tp.Any]:

        @functools.wraps(func)
        def wrapper_func(*args: tp.Any, **kwargs: tp.Any) -> tp.Any:
            __check_required_args_impl(required_args, kwargs)
            return func(*args, **kwargs)

        return wrapper_func

    return decorator_pp


def find_missing_revisions(
        data: tp.Generator[tp.Any, None, None], git_path: Path, cmap: CommitMap,
        should_insert_revision: tp.Callable[[tp.Any, tp.Any], tp.
                                            Tuple[bool, float]],
        to_commit_hash: tp.Callable[[tp.Any], str],
        are_neighbours: tp.Callable[[str, str], bool]) -> tp.Set[str]:
    """
    Calculate a set of revisions that could be missing because the changes
    between certain points are to steep.
    """
    new_revs: tp.Set[str] = set()

    _, last_row = next(data)
    for _, row in data:
        should_insert, gradient = should_insert_revision(last_row, row)
        if should_insert:
            lhs_cm = to_commit_hash(last_row)
            rhs_cm = to_commit_hash(row)

            if are_neighbours(lhs_cm, rhs_cm):
                print("Found steep gradient between neighbours " +
                      "{lhs_cm} - {rhs_cm}: {gradient}".format(
                          lhs_cm=lhs_cm,
                          rhs_cm=rhs_cm,
                          gradient=round(gradient, 5)))
                print("Investigate: git -C {git_path} diff {lhs} {rhs}".format(
                    git_path=git_path, lhs=lhs_cm, rhs=rhs_cm))
            else:
                print("Unusual gradient between " +
                      "{lhs_cm} - {rhs_cm}: {gradient}".format(
                          lhs_cm=lhs_cm,
                          rhs_cm=rhs_cm,
                          gradient=round(gradient, 5)))
                new_rev_id = round(
                    (cmap.short_time_id(lhs_cm) + cmap.short_time_id(rhs_cm)) /
                    2.0)
                new_rev = cmap.c_hash(new_rev_id)
                print(
                    "-> Adding {rev} as new revision to the sample set".format(
                        rev=new_rev))
                new_revs.add(new_rev)
        last_row = row
    return new_revs


def bisect_project(
        data: tp.Set[str], project: str,
        should_insert_revision: tp.Callable[[str, str], tp.Tuple[bool, float]]
) -> tp.Set[str]:
    """
    Perform a bisection step over the whole history of a project for a given
    sample of evaluated revisions.
    
    Args:
        data: The set of revisions used for bisection.
        project: The project to bisect on.
        should_insert_revision: A function that, given two revisions, determines
                                whether bisection should be performed at that
                                point.

    Returns: A set of revisions that should be evaluated for the next
             bisection step.
    """

    new_revs: tp.Set[str] = set()
    repo = get_local_project_git(project)
    git = create_git_project_wrapper(project)

    def next_commits(head_commit: pygit2.Commit) -> tp.Set[pygit2.Commit]:
        queue: tp.List[pygit2.Commit] = head_commit.parents
        visited: tp.Set[pygit2.Commit] = set(head_commit.parents)
        result: tp.Set[pygit2.Commit] = set()

        while queue:
            c = queue.pop()
            if str(c.id) in data:
                result.add(c)
            else:
                for p in c.parents:
                    if p not in visited:
                        queue.append(p)
                        visited.add(p)

        return result

    to_process = list(next_commits(repo.revparse_single('HEAD')))
    processed = set(to_process)
    while to_process:
        current_commit = to_process.pop()
        next_set = next_commits(current_commit)

        should_bisect = any([
            should_insert_revision(str(commit.id), str(current_commit.id))[0]
            for commit in next_set
        ])

        if should_bisect:
            print(f"Bisecting at commit {current_commit.id}:")
            good = set([
                c for c in next_set if should_insert_revision(
                    str(c.id), str(current_commit.id))[0] is True
            ])

            # returns the commit hash that git-bisect would return
            # if current_commit was marked as `bad` and the commits in
            # good were marked as `good`
            new_rev = repo.get(
                git("rev-list", "--bisect", f"{str(current_commit.id)}",
                    *[f"^{str(g.id)}" for g in good]).strip())
            if str(new_rev.id) not in data:
                print(f"-> Adding {new_rev.id} as new revision to the " +
                      f"sample set")
                new_revs.add(str(new_rev.id))
            else:
                print("-> Bisection point already evaluated. Skipping.")
        for n in next_set:
            if n not in processed:
                to_process.append(n)
                processed.add(n)
    return new_revs
