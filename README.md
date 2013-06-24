A collection of tools for managing and creating AWS Machine Images

If your AWS workflow involves creating many AMIs (machine images), on
a weekly, daily, or even hourly basis, managing them becomes a
logistical nightmare. Born from hard experience, AMITools solves many
of the toughest problems in this situation: letting you quickly answer
questions about the relationships between your AMIs, their history,
and current status... making its logistic complexity far more simple.

At the moment (June 2013), it is in a beta. I'd appreciate feedback
especially on the command line UI, and also reports of bugs or missing
functionality not called out in the text below. (I'm updating this
README as I go along.) Message me via github, or (preferred) send
email to amax at redsymbol dot net. You can also follow me as
[@redsymbol](https://twitter.com/redsymbol) on twitter.

# What's In The Box

 - ami-create-image - Like ec2-create-image, but way better
 - ami-waiton - Wait for the image to reach a useful state * 
 - ami-describe-ancestors - What images are this image derived from? *
 - ami-tag-image - Tag an existing image like ami-create-image does

(Items marked with "*" are mostly but not yet completely implemented.)

And coming soon (see README.future.md for details):
 - ami-describe-children - Show what images are derived from this one
 - ami-clone - Clone an image so you always have your own version
 - ami-copy-image - Copy an AMI from one region to another

## Installation

Stand by for easy installation via "pip install amitools". In the
meantime:

Get the sources, either via git clone or downloading a snapshot, here
on github. Set your environment so the full path of the folder
amitools/bin is in your PATH, and amitools/lib is in your PYTHONPATH.

You must also install boto; "pip install boto" will do the job for
you.  Any recent version should be fine; see requirements.txt for the
version that the developer is using (and testing on).

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

# Image Tags

The AMITools work with a standard set of tags on each AMI, defining
the image's heritage and geneology.  These are set automatically by
ami-create-image, or you can set or change them manually with
ami-tag-image. The tags include:

<dl>
  <dt>source_image</dt>
  <dd>The AMI ID of the instance from which it was created</dd>
  <dt>source_instance</dt>
  <dd>The instance ID from which it was created</dd>
  <dt>source_region</dt>
  <dd>Region of the source AMI</dd>
  <dt>create_date</dt>
  <dd>When it was created (human-readable)</dd>
  <dt>create_timestamp</dt>
  <dd>When it was created (seconds since epoch)</dd>
</dl>


(create_date and create_timestamp encode the same information, just
represented in two differently convenient formats.)

This information is helpful and useful all by itself. It's
used to even greater effect by other tools in this package - both
current, and planned for the near future.

# Command Descriptions

Unless noted otherwise, each command takes a -r/--region option. If
supplied, this overrides the region specified using one of the methods
above.  All commands take an -h/--help option explaining how to use
the tool.

## ami-create-image

This is similar to the ec2-create-image command from the AWS command
line tools, with some differences: 

 - Automatically tag images with delicious and valuable info
 - Optionly generate unique, random new AMI name for you

The tags are described above, in "Image Tags".

### Auto-Naming

If you are generating images with any frequency, you have probably
been annoyed by the requirement to supply a unique name for each image
you create. Once you get to the point where you are creating several
images per week, or even per day, some teams find it easier to simply
keep track of the AMI IDs rather than referencing the name.

If you want to grant an explicit name, do so with the -n/--name
option. But if you do not, ami-create-image generates a random name
for the image, with a format like:

    <prefix>-<timestamp>-<big random number>

(Note that this auto-naming is the default behavior, unless you specify
an explicit name with -n/--name.)

"timestamp" is the number of seconds since the epoch - an integer. By
default, the prefix is unimaginatively "AMI", which means names are
generated that look like (for example)
"AMI-1366162881-135159873121564".  Choose a different prefix by giving
-N or --random-name-prefix an argument (these two options are completely
interchangeable):

    ami-create-image --random-name-prefix database i-12345678 

This will give the new image a name like
"database-1366162881-135159873121564".  It can be useful for easy type
classification of AMIs based on their name.

(In the highly unlikely event the first generated name is taken,
ami-create-image will keep generating a new name until it finds a
unique one.)

## ami-waiton

(mostly implemented; the --dumb option is not yet done)

ami-waiton robustly waits for an AMI to be in a particular
state, intelligently handling latency and race conditions.

Use it like:

    ami-waiton [--dumb] [ --nowait-exist ] AMI_ID [STATE]

where STATE is one of "available", "pending", "failed" or "exists".
The default value is "available", because very often, when using this
command, you will just want to block until the AMI is in the available
state.

By default, some intelligence is applied. If you specify "available",
and the AMI is in state "failed", it will never be available;
ami-waiton exits with a error code.  Similar if you specify "pending"
as the target state.

If you'd like this magic disabled, use the --dumb option. This will
strictly interpret the state argument.

The state of "exists" just means "this AMI is in any state at
all". Sometimes, there is a delay between the time in which you create
the AMI and when it is readable at all by the Amazon API: a kind of
"pre-pending" state in which a query to list all pending images may
not include the new one - even though the create command you just
issued already gave you the AMI ID.

By default, if this initially happens, ami-waiton assumes the image is
still in the pre-pending state, and will keep re-checking for some
time before giving up.

For automating AMI operations in scripts, where robustness is
typically way more important than execution time, this is the
preferred behavior. If you want to disable this check, use the
--nowait-exist option. This will cause ami-waiton to exit with an
error if the AMI isn't immediately visible.  (This option is only
supported with states other than "exist", because that's what makes
sense.)

## ami-describe-ancestors
(partially implemented; only shows image IDs, not other columns yet)

ami-describe-ancestors answers questions like:

 - What image was this image derived from?
 - What was the "grandparent" image? And the one before that?
 - When did all the above happen?

There is a prerequisite: it only works with images that were created
via ami-create-images, or those AMIs that are externally tagged in the
same way ami-create-images does. If you build a toolchain that creates
your AMIs via ami-create-images, ami-describe-ancestors can tell you
where any image ID sits in the hierarchy.

Usage:

    ami-describe-ancestors [-C|--columns] START_AMI_ID

If invoked with a START_AMI_ID value of ami-55555555, This may show something like:

    IMAGE_ID      CREATE_DATE                   CREATE_TS  SOURCE_INSTANCE
    ami-55555555  Thu Apr 17 18:17:56 UTC 2013  1366222705 i-55555555
    ami-44444444  Thu Apr 16 18:17:56 UTC 2013  1366136305 i-44444444
    ami-33333333  Thu Apr 15 18:17:56 UTC 2013  1366049905 i-33333333

What this indicates is that ami-55555555 was created from an instance
run from ami-44444444. The image-creation operation was invoked on
instance i-44444444, on April 16th 2013.  This output also reveals
that ami-44444444 was created from an instance run from i-33333333,
and so on.

# ami-tag-image

ami-tag-image lets you set the standard AMITools tags on any image, in
a way that's more convenient and robust than setting them
manually. This has several uses.

When you create a new image via ami-create-image, these tags are set
automatically.  And if that is the only way you ever create images,
you won't have to use ami-tag-image.  But suppose you have some
important AMIs that were created before then; or, you need to continue
generating new images using a different technique (there are many
valid reasons for this).

ami-tag-image applies in all these situations. It has flags used to
set the correct values for each of the required tags, with some handy
error-checking.

The options:

    --source-image SOURCE_IMAGE
        Image ID of source AMI
        (tag: source_image)
    --source-instance SOURCE_INSTANCE
        ID of source instance
        (tag: source_instance)
    --source-region SOURCE_REGION
        Region for the source AMI
        (tag: source_region)
    --create-date CREATE_DATE
        Creation date, in UTC/GMT, like "20110909T233600Z"
        (tag: create_date)
    --create-timestamp CREATE_TIMESTAMP
        Creation timestamp, in seconds since the epoch
        (tag: create_timestamp)

You supply exactly one of --create-timestamp or --create-date, but NOT
both. The value of the other will be calculated automatically by the
one you supply.

# Author

Created by [Aaron Maxwell](http://redsymbol.net). To give feedback,
bug reports, complaints, praise, etc., contact him at amax at
redsymbol dot net .

Aaron is selectively available as a consultant for AWS/cloud migration
and architecture projects; reach him at the same email address.

# License

Copyright 2013 Aaron Maxwell. Licensed under GPL v.3. 
All other rights reserved.
