# image-directory-preview
<!------------------------------------------------------------------------>
Preview images from a directory containing many images using the Python
package napari

## FFMpeg command:
<!------------------------------------------------------------------------>
The following command will create an MP4 video out of all the images at the
location `path/to/images/` with a title that begins with `image_prefix_` and
ends with a number with leading zeros that make the number three characters
long and a file suffix `.png`. The video will have the replay framerate of
10 fps. The option `-pix_fmt yuv420p` specifies a pixel format that works
well for MP4 videos.
```
ffmpeg -r 10 -i path/to/images/image_prefix_%03d.png -pix_fmt yuv420p
path/to/video/video_name.mp4
```
