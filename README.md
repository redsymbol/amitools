A collection of tools for joyfully working with AWS Machine Images

AMITools is a collection of command-line tools for creating, querying,
and working with Amazon machine images.

# What's In The Box

 - ami-create-image - Like ec2-create-image, but way better
 - ami-waiton - Wait for the image to reach a useful state
 - ami-describe-anscestors - What images are this image derived from?
 - ami-describe-children - What images are derived from this image?
 - ami-tag-image - Tag an existing image like ami-create-image does

## Credentials & Region Setup

To use these tools, you must first specify your AWS credentials and
default region. You can do this with environment variables, or a
credentials file.

### Environment Method

Export the following definitions in your shell environment:
  AWS_ACCESS_KEY_ID=<your access key>
  AWS_SECRET_ACCESS_KEY=<your secret key>
  AWS_DEFAULT_REGION=<code for default region>

(Make sure they are exported. So in bash, for example, that means
using the "export" keyword.)

### Credential File Method

Create a file whose content looks like this:

  aws_access_key_id=<your access key>
  aws_secret_access_key=<your secret key>
  region=<code for default region>

Make sure it is not world-readable. Then, export the full path to this
file in the environment variable AWS_CREDENTIAL_FILE. 

(Make sure it is exported. So in bash, for example, that means using
the "export" keyword.)

# Command Descriptions

Unless noted otherwise, each command takes the following options:

  - -r/--region  Operate on the given region

## ami-create-image
(not implemented yet)

This is similar to the ec2-create-image command from the AWS command
line tools, with some differences: 

 - Automatically tag images with delicious and valuable info
 - Optionly generate unique, random new AMI name for you

### Image Tags

ami-create-image tags the AMI with information about its heritage and
geneology. These include:

 - source_image       The AMI ID of the instance from which it was created
 - source_instance    The instance ID from which it was created
 - create_date        When it was created (human-readable)
 - create_timestamp   When it was created (seconds since epoch)

### Auto-Naming

If you are generating images with any frequency, you have probably
been annoyed by the requirement to supply a unique name for each image
you create. Once you get to the point where you are creating several
images per week, or even per day, some people find it easier to simply
keep track of the AMI IDs rather than referencing the name.

By using the -N or --random-name options, ami-create-image will
generate a unique AMI name for you. You can optionally specify a
prefix for that name.  For example:

  ami-create-image -N i-12345678 

This will generate a completely random unique name, something like
"AMI-1366162881-135159873121564" By default, the prefix is
unimaginatively "AMI". Choose a different prefix by giving -N or
--random-name an argument (these two options are completely
interchangeable):

  ami-create-image --random-name database i-12345678 

This will give the new image a name like
"database-1366162881-135159873121564".  It can be useful for easy type
classification.

The format of the name is like:

  <prefix>-<timestamp>-<big random number>

timestamp is the number of seconds since the epoch - an integer. (In
the highly unlikely event the first generated name is taken,
ami-create-image will generating a new name until it finds a unique one.)

## ami-waiton and ami-waiton-available
(not implemented yet)

Robustly wait on an AMI to be in a particular state. Intelligently
handle latency and race conditions.

ami-waiton is the generic form. Use it like:

  ami-waiton [--dumb] [ --nowait-exist ] AMI_ID STATE

Where STATE is one of "available", "pending" or "failed" or
"exists". The state of "exists" just means "this AMI is in any state
at all".

By default, some intelligence is applied. If you specify "available",
and the AMI is in state "failed", it will never be available;
ami-waiton exits with a error code.  If you specifiy "pending", and
the current state is "available", it returns immediately with a
success code; the rationale is that "ami-waiton AMI_ID pending" really
means, "wait until it is in the pending state, or better."

If you'd like this magic disabled, use the --dumb option. This will
strictly interpret the state argument.

Sometimes, there is a delay between the time in which you create the
AMI and when it is readable at all by the Amazon API.  In other words,
there is a "pre-pending" state in which a query to list all pending
images may not include the new one - even though the create command
you just issued already gave you the AMI ID.

By default, if this initially happens, ami-waiton assumes that the AMI
is still in the pre-pending state, and will keep re-checking for some
time before giving up.

For automating AMI operations in scripts, where robustness is
typically way more important than execution time, this is the
preferred behavior. If you want to disable this check, use the
--nowait-exist option. This will cause ami-waiton to exit with an
error if the AMI isn't immediately visible.

Very often, when using this command, you just want to block until the
AMI is in an available state.  Use ami-waiton-available as a
shortcut. Use it like:

  ami-waiton-available AMI_ID

This is exactly equivalent to "ami-waiton AMI_ID available" with no
options. It has the same defaults as ami-waiton (the aforementioned
intelligence, and waiting through the pre-pending state), but these
cannot be disabled. If you need that, use ami-waiton instead.

## ami-describe-anscestors
(not implemented yet)

ami-describe-anscestors answers questions like:

 - What image was this image derived from?
 - What was the "grandparent" image? And the one before that?
 - When did all the above happen?

There is a prerequisite: it only works with images that were created
via ami-create-images, or those AMIs that are externally tagged in the
same way ami-create-images does. If you build a toolchain that creates
your AMIs via ami-create-images, ami-describe-family can tell you
where any image ID sits in the hierarchy.

Usage:
  ami-describe-family [-C|--columns] START_AMI_ID

If invoked with a START_AMI_ID value of ami-55555555, This may show something like:
IMAGE_ID      CREATE_DATE                   CREATE_TS  SOURCE_INSTANCE
ami-33333333  Thu Apr 15 18:17:56 UTC 2013  1366049905 i-33333333
ami-44444444  Thu Apr 16 18:17:56 UTC 2013  1366136305 i-44444444
ami-55555555  Thu Apr 17 18:17:56 UTC 2013  1366222705 i-55555555

What this indicates is that ami-55555555 was created from an instance
run from ami-44444444. The image-creation operation was invoked on
instance i-44444444, on April 16th 2013.  This output also reveals
that ami-44444444 was created from an instance run from i-33333333,
and so on.

## ami-describe-children
(not implemented yet)

ami-describe-children answers questions like:

 - What images were created from instances running this image?
 - What are the known "grandchildren" images, and so on?
 - When did all the above happen?

Like ami-describe-anscestors, it works only with images that were
created via ami-create-images, or those AMIs that are externally
tagged in the same way ami-create-images does - for the same reasons.

## ami-tag-image
(not implemented yet)

Tags an existing image in the same way that ami-create-image does. You
must supply all the values yourself.

# Author

[Aaron Maxwell](http://redsymbol.net). To give bug reports,
complaints, praise, massive cash donations, etc., contact him at
amax@redsymbol.net .

# License

Copyright 2013 Aaron Maxwell. Licensed under GPL v.3. 
All other rights reserved.