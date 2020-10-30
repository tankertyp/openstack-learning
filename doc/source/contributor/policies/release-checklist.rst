Pre-release check list
======================

This page lists things to cover before a Neutron release and will serve as a
guide for next release managers.

Server
------

Major release
~~~~~~~~~~~~~

A Major release is cut off once per development cycle and has an assigned name
(Liberty, Mitaka, ...)

Prior to major release,

#. consider blocking all patches that are not targeted for the new release;
#. consider blocking trivial patches to keep the gate clean;
#. revise the current list of blueprints and bugs targeted for the release;
   roll over anything that does not fit there, or won't make it (note that no
   new features land in master after so called feature freeze is claimed by
   release team; there is a feature freeze exception (FFE) process described in
   release engineering documentation in more details:
   http://docs.openstack.org/project-team-guide/release-management.html);
#. start collecting state for targeted features from the team. For example,
   propose a post-mortem patch for neutron-specs as in:
   https://review.opendev.org/#/c/286413/
#. revise deprecation warnings collected in latest Jenkins runs: some of them
   may indicate a problem that should be fixed prior to release (see
   deprecations.txt file in those log directories); also, check whether any
   Launchpad bugs with the 'deprecation' tag need a clean-up or a follow-up in
   the context of the release being planned;
#. check that release notes and sample configuration files render correctly,
   arrange clean-up if needed;
#. ensure all doc links are valid by running ``tox -e linkcheck`` and
   addressing any broken links.

New major release process contains several phases:

#. master branch is blocked for patches that are not targeted for the release;
#. the whole team is expected to work on closing remaining pieces targeted for
   the release;
#. once the team is ready to release the first release candidate (RC1), either
   PTL or one of release liaisons proposes a patch for openstack/releases repo.
   For example, see: https://review.opendev.org/#/c/292445/
#. once the openstack/releases patch lands, release team creates a new stable
   branch using hash values specified in the patch;
#. at this point, master branch is open for patches targeted to the next
   release; PTL unblocks all patches that were blocked in step 1;
#. if additional patches are identified that are critical for the release and
   must be shipped in the final major build, corresponding bugs are tagged
   with <release>-rc-potential in Launchpad, fixes are prepared and land in
   master branch, and are then backported to the newly created stable branch;
#. if patches landed in the release stable branch as per the previous step, a
   new release candidate that would include those patches should be requested
   by PTL in openstack/releases repo;
#. eventually, the latest release candidate requested by PTL becomes the final
   major release of the project.

Release candidate (RC) process allows for stabilization of the final release.

The following technical steps should be taken before the final release is cut
off:

#. the latest alembic scripts are tagged with a milestone label. For example,
   see: https://review.opendev.org/#/c/288212/

In the new stable branch, you should make sure that:

#. .gitreview file points to the new branch;
#. if the branch uses constraints to manage gated dependency versions, the
   default constraints file name points to corresponding stable branch in
   openstack/requirements repo;
#. if the branch fetches any other projects as dependencies, e.g. by using
   tox_install.sh as an install_command in tox.ini, git repository links point
   to corresponding stable branches of those dependency projects.

Note that some of those steps may be covered by the OpenStack release team.

In the opened master branch, you should:

#. update CURRENT_RELEASE in neutron.db.migration.cli to point to the next
   release name.

While preparing the next release and even in the middle of development, it's
worth keeping the infrastructure clean. Consider using these tools to declutter
the project infrastructure:

#. declutter Gerrit::

    <neutron>/tools/abandon_old_reviews.sh

#. declutter Launchpad::

    <release-tools>/pre_expire_bugs.py neutron --day <back-to-the-beginning-of-the-release>


Minor release
~~~~~~~~~~~~~

A Minor release is created from an existing stable branch after the initial
major release, and usually contains bug fixes and small improvements only.
The minor release frequency should follow the release schedule for the current
series. For example, assuming the current release is Rocky, stable branch
releases should coincide with milestones R1, R2, R3 and the final release.
Stable branches can be also released more frequently if needed, for example,
if there is a major bug fix that has merged recently.

The following steps should be taken before claiming a successful minor release:

#. a patch for openstack/releases repo is proposed and merged.


Minor version number should be bumped always in cases when new release contains
a patch which introduces for example:

#. new OVO version for an object,
#. new configuration option added,
#. requirement change,
#. API visible change,

The above list doesn't cover all possible cases. Those are only examples of fixes
which require bump of minor version number but there can be also other types of
changes requiring the same.

Changes that require the minor version number to be bumped should always have a
release note added.

In other cases only patch number can be bumped.


Client
------

Most tips from the Server section apply to client releases too. Several things
to note though:

#. when preparing for a major release, pay special attention to client bits
   that are targeted for the release. Global openstack/requirements freeze
   happens long before first RC release of server components. So if you plan to
   land server patches that depend on a new client, make sure you don't miss
   the requirements freeze. After the freeze is in action, there is no easy way
   to land more client patches for the planned target. All this may push an
   affected feature to the next development cycle.
