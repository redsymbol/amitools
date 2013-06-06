## ami-describe-children
(not implemented yet)

ami-describe-children answers questions like:

 - What images were created from instances running this image?
 - What are the known "grandchildren" images, and so on?
 - When did all the above happen?

Like ami-describe-ancestors, it works only with images that were
created via ami-create-images, or those AMIs that are externally
tagged in the same way ami-create-images does - for the same reasons.

## ami-clone
(not implemented yet)

ami-clone makes a copy of an image. It functions similar to
[CopyImage](http://docs.aws.amazon.com/AWSEC2/latest/APIReference/ApiReference-query-CopyImage.html)
or
[ec2-copy-image](http://docs.aws.amazon.com/AWSEC2/latest/CommandLineReference/ApiReference-cmd-CopyImage.html),
but instead of making a copy in a new region, it makes a copy in the
source image's region - with a new AMI ID.

Why would you want to do this? As far as I know, there is only one
good reason, but it's a very important one. If you are creating a tree
of images which use a public AMI supplied by a third party, it's wise
to make your own copy in case the third-party creator someday decides
to withdraw the original.

In other words, here's what you do NOT want to happen:

 1. You are building a server based off of Ubuntu, or Red Hat, or
    whatever, and you get an AMI ID of their distribution off of their
    website. Call this the "foundation image".

 1. You create a series of tools to build a half-dozen different image
    types, all based on the foundation, and whose instances support
    everything from web servers to database services to devops
    orchestration to bastion services and more.  All these tools are
    in version control, allowing you to rebuild them at any time... as
    long as you can run instances from the foundation image.

 1. Suddenly, unexpectedly, the third party decides to revoke the
    foundation image. Now you can't rebuild things from scratch until
    you cobble together some foundation image of your own, and be
    ready to spend the next few months uncovering and troubleshooting
    legions of obscure bugs.

If you create your own, private clone, and use **that** as the
foundation, the last step will happen to your competitors instead of
you.

In addition, ami-clone will give the new image the same tags as the
other images created by amitools, so you always know where (and when)
it fits in your AMI hierarchy.

## ami-copy-image
(not implemented yet)

ami-copy-image copies an AMI from one region to another. It is exactly
like
[ec2-copy-image](http://docs.aws.amazon.com/AWSEC2/latest/CommandLineReference/ApiReference-cmd-CopyImage.html),
but also sets the standard AMITools tags. It also sets one other:
source_region, whose value will be a region code like "us-east-1" or "ap-southeast-1".

Usage:

    ami-copy-image -r SOURCE_REGION -s SOURCE_AMI_ID [OPTS ...]

The options include:
    -R, --dest-region    DEST_REGION
    -n, --name           AMI_NAME
    --random-name-prefix PREFIX
    -d, --description    DESCRIPTION

The destination region defaults to the current region, as defined by
AWS_DEFAULT_REGION or the "region" setting in the credentials file.

You'll notice that, unlike ec2-create-image, the -n/--name option is
optional. By default, a random AMI name is generated for you, the same
as in ami-create-image. You can also specify a prefix for the random
name via --random-name-prefix. See the section on ami-create-image for details.

# TODOs

Make ami-describe-ancestors and ami-describe-children aware of
cross-region copies. Do we want this to be controlled by an option? If
so, what's the default?

I think I need to set the source_region tag in the default tag set,
i.e. all AMIs created via amitools will have that, even if they are
only ever used in the same region. Would make all the cross-region
stuff a lot simpler.
