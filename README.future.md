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
must supply the values yourself.

This is used when you have a pre-existing AMI which you want to work
together with amitools; by giving it the right tag values, it can
integrate just as if it was created by ami-create-image.

