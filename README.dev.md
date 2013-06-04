# Dev Notes

This is information for people who want to understand or modify the source code.

## Tests

There are two top-level folders, named tests/ and inttests/ . The
former includes unit tests (depending on your definition of that
term): any test that can be run without actually invoking the AWS
API.  They run relatively fast, and do not require access to live API
credentials.

The inttests/ folder contains integration tests, defined here as those
tests which actually will create resources in your AWS account. This
process (and the cleanup) is managed by the
amitools.test.InstanceTestCase class, a subclass of unittest.TestCase.

For these integration tests to run, you must export your AWS
credentials and some other settings in your environment. At the moment
this is documented in the InstanceTestCase class of
lib/amitools/test.py, so please see that file for details. 

You can run tests with nose.  To run the unit tests:

    nosetests tests/

And the integration tests:

    nosetests inttests/

Or both:

    nosetests tests/ inttests/

If you do run the integration tests, please read this next section on the
integration test process first.

### More on amitool's integration test process

InstanceTestCase will start dummy EC2 instances. It attempts to
terminate this no matter what, and goes to heroic lengths to make sure
this happens regardless of what code you might put in your test
method.  Regardless, it is not impossible that resource leaks occur,
for example if the test process is terminated with prejudice
(e.g. with a kill -9) before that cleanup has a chance to occur, or
perhaps even due to a bug I have missed. 

This is obviously a hazard to your monthly AWS bill. Please exercise
some care and check that no stray EC2 instances are running after you
are done with your testing.

(If you do find a reproducible leak, please let me know - my direct
contact info is in the "Author" section below.)

## Code Structure

The executables in bin/ are thin wrappers around a dedicated module in
amitools.tools; for example, most of the code for
ami-describe-anscestors is in
lib/amitools/tools/ami_describe_anscestors.py (and the modules it
imports). These executables import a "get_args" and a "main" callable
from its corresponding amitools.tools module, and possibly some other
symbols. If you want to look at what one of the executables is doing,
start by looking at the source of its main(). Generally, as much
actual code as possible is kept under lib/amitools/ .

