# GameChanger Video Downloader

This is a project to allow a user to download GameChanger Full Event Videos to their local machine.

## Why

While I love streaming my kid's sports on the GameChanger app, I became increasingly frustrated with having to record on multiple devices in order to share video/clips outside of the livestream.  This tool was built to fetch the highest quality video that was streamed for any event that the user can access.

## [WIP] Authentication

This is still a work in progress as I'm still working on reverse engineering the authentication process for GameChanger.

For now, you'll need to export your GameChanger token as the `GC_TOKEN` environment variable.  If you don't know how to get this, or set it, this project probably isn't for you at the moment.

## Docker

This application can be run as an isolated Docker container.  The image is currently stored on Docker Hub at `alannix/gamechanger-video-downloader`.

There are two configuration items you'll want to set up before running the container:
- You'll need to pass through a directory from your local machine for storing videos with the `-v` flag.  Videos are stored in the `/app/videos` directory within the container.
- You'll need to pass through the `GC_TOKEN` environment variable to authenticate to GameChanger.

An example command will look like this:
```
docker run -it -v ./videos:/app/videos -e GC_TOKEN=<GAMECHANGER TOKEN HERE> alannix/gamechanger-video-downloader:latest
```

## Video Format

The downloaded video will be stored as a MPEG Transport Stream (.ts) file.  Platforms such as YouTube understand this format natively, but many media players do not.  You can use tools such as [FFmpeg](https://www.ffmpeg.org/) or [Handbrake](https://handbrake.fr/) to losslessly convert the video.

### Examples

#### FFmpeg
```
ffmpeg -i stream_1.ts my_output_video.mp4
```

#### HandbrakeCLI
```
handbrakeCLI -i stream_1.ts -o my_output_video.mp4 -f av_mp4
```
