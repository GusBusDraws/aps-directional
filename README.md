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
ffmpeg -r 10 -i path/to/images/image_prefix_%03d.png -pix_fmt yuv420p -vf "crop='iw-mod(iw,2)':'ih-mod(ih,2)'" path/to/video/video_name.mp4
```

Alternatively, you can set an experiment name:
```
exp=experimentName && ffmpeg -r 10 -i path/to/parent/$exp/$exp_%03d.png -vf "crop='iw-mod(iw,2)':'ih-mod(ih,2)'" -pix_fmt yuv420p path/to/save/location/$exp.mp4
```

However, these commands will only work if the frame images each end with a
three-digit number (padded with zeros). For a two digit number, the filename
`%03d` in the filename would need to be replaced with `%02d`.
