import asyncio
import subprocess
import shutil
import os
import time
from pyrogram.types import CallbackQuery
from pyrogram.types import Message
from config import Config
from __init__ import LOGGER
from helpers.utils import get_path_size


async def MergeVideo(input_file: str, user_id: int, message: Message, format_: str):
    """
    Merge multiple video files into a single MKV file using mkvmerge.
    :param `input_file`: Path to the input file list.
    :param `user_id`: User ID for output path.
    :param `message`: Message object to update status.
    :param `format_`: File extension for the output file.
    :return: Merged video file path or None if merging failed.
    """
    output_vid = f"downloads/{str(user_id)}/[@yashoswalyo].{format_.lower()}"
    file_generator_command = [
        "mkvmerge",
        "-o",
        output_vid,
        "--output-headers",
        "0",
        "-f",
        "concat",
        "--file-list",
        input_file
    ]
    
    process = None
    try:
        process = await asyncio.create_subprocess_exec(
            *file_generator_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except NotImplementedError:
        await message.edit(
            text="Unable to Execute mkvmerge Command! Got `NotImplementedError` ...\n\nPlease run bot in a Linux/Unix Environment."
        )
        await asyncio.sleep(10)
        return None
    
    await message.edit("Merging Video Now ...\n\nPlease Keep Patience ...")
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    LOGGER.info(e_response)
    LOGGER.info(t_response)
    
    if os.path.lexists(output_vid):
        return output_vid
    else:
        return None


def MergeSub(filePath: str, subPath: str, user_id):
    """
    Merge video file with subtitle using mkvmerge.
    :param filePath: Path to the video file.
    :param subPath: Path to the subtitle file.
    :param user_id: User ID for output path.
    :return: Merged video file path.
    """
    LOGGER.info("Generating mux command")
    muxcmd = [
        "mkvmerge",
        "-o",
        f"./downloads/{str(user_id)}/[@yashoswalyo]_softmuxed_video.mkv",
        filePath,
        subPath
    ]
    
    LOGGER.info("Muxing subtitles")
    subprocess.call(muxcmd)
    
    orgFilePath = shutil.move(
        f"./downloads/{str(user_id)}/[@yashoswalyo]_softmuxed_video.mkv", filePath
    )
    return orgFilePath


def MergeSubNew(filePath: str, subPath: str, user_id, file_list):
    """
    Merge video file with multiple subtitles using mkvmerge.
    :param filePath: Path to the video file.
    :param subPath: Path to subtitle files.
    :param user_id: User ID for output path.
    :param file_list: List of input files.
    :return: Path to the merged file.
    """
    LOGGER.info("Generating mux command")
    muxcmd = ["mkvmerge", "-o", f"./downloads/{str(user_id)}/[@yashoswalyo]_softmuxed_video.mkv"]
    muxcmd.append(filePath)
    
    for i in file_list:
        muxcmd.extend(["--language", f"0:{i}", i])
    
    LOGGER.info("Sub muxing")
    subprocess.call(muxcmd)
    
    return f"downloads/{str(user_id)}/[@yashoswalyo]_softmuxed_video.mkv"


def MergeAudio(videoPath: str, files_list: list, user_id):
    """
    Merge audio tracks from files into a video file using mkvmerge.
    :param videoPath: Path to the video file.
    :param files_list: List of audio files to merge.
    :param user_id: User ID for output path.
    :return: Path to the merged file.
    """
    LOGGER.info("Generating Mux Command")
    muxcmd = ["mkvmerge", "-o", f"downloads/{str(user_id)}/[@yashoswalyo]_export.mkv", videoPath]
    
    for i in files_list:
        muxcmd.extend(["--audio-tracks", i])
    
    LOGGER.info(muxcmd)
    subprocess.call(muxcmd)
    
    return f"downloads/{str(user_id)}/[@yashoswalyo]_export.mkv"


async def cult_small_video(video_file, output_directory, start_time, end_time, format_):
    """
    Generate a small cut of the video using mkvmerge.
    :param video_file: Path to the video file.
    :param output_directory: Directory to save the output file.
    :param start_time: Start time for cutting the video.
    :param end_time: End time for cutting the video.
    :param format_: File format for the output file.
    :return: Path to the cut video file.
    """
    out_put_file_name = (
        output_directory + str(round(time.time())) + "." + format_.lower()
    )
    file_generator_command = [
        "mkvmerge",
        "-o",
        out_put_file_name,
        "--split",
        f"timecodes:{start_time}-{end_time}",
        video_file
    ]
    process = await asyncio.create_subprocess_exec(
        *file_generator_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    LOGGER.info(e_response)
    LOGGER.info(t_response)
    
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None


async def take_screen_shot(video_file, output_directory, ttl):
    """
    This functions generates custom_thumbnail / Screenshot.

    Parameters:

    - `video_file`: Path to video file.
    - `output_directory`: Path where to save thumbnail
    - `ttl`: Timestamp to generate ss

    returns: This will return path of screenshot
    """
    # https://stackoverflow.com/a/13891070/4723940
    out_put_file_name = os.path.join(output_directory, str(time.time()) + ".jpg")
    if video_file.upper().endswith(
        (
            "MKV",
            "MP4",
            "WEBM",
            "AVI",
            "MOV",
            "OGG",
            "WMV",
            "M4V",
            "TS",
            "MPG",
            "MTS",
            "M2TS",
            "3GP",
        )
    ):
        file_genertor_command = [
            "ffmpeg",
            "-ss",
            str(ttl),
            "-i",
            video_file,
            "-vframes",
            "1",
            out_put_file_name,
        ]
        # width = "90"
        process = await asyncio.create_subprocess_exec(
            *file_genertor_command,
            # stdout must a pipe to be accessible as process.stdout
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        # Wait for the subprocess to finish
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()
    #
    if os.path.exists(out_put_file_name):
        return out_put_file_name
    else:
        return None


async def extractAudios(path_to_file, user_id):
    """
    docs
    """
    dir_name = os.path.dirname(os.path.dirname(path_to_file))
    if not os.path.exists(path_to_file):
        return None
    if not os.path.exists(dir_name + "/extract"):
        os.makedirs(dir_name + "/extract")
    videoStreamsData = ffmpeg.probe(path_to_file)
    # with open("data.json",'w') as f:
    #     f.write(json.dumps(videoStreamsData))
    extract_dir = dir_name + "/extract"
    audios = []
    for stream in videoStreamsData.get("streams"):
        try:
            if stream["codec_type"] == "audio":
                audios.append(stream)
        except Exception as e:
            LOGGER.warning(e)
    for audio in audios:
        extractcmd = []
        extractcmd.append("ffmpeg")
        extractcmd.append("-hide_banner")
        extractcmd.append("-i")
        extractcmd.append(path_to_file)
        extractcmd.append("-map")
        try:
            index = audio["index"]
            extractcmd.append(f"0:{index}")
            try:
                output_file: str = (
                    "("
                    + audio["tags"]["language"]
                    + ") "
                    + audio["tags"]["title"]
                    + "."
                    + audio["codec_type"]
                    + ".mka"
                )
                output_file = output_file.replace(" ", ".")
            except:
                output_file = str(audio["index"]) + "." + audio["codec_type"] + ".mka"
            extractcmd.append("-c")
            extractcmd.append("copy")
            extractcmd.append(f"{extract_dir}/{output_file}")
            LOGGER.info(extractcmd)
            subprocess.call(extractcmd)
        except Exception as e:
            LOGGER.error(f"Unable to extract audio {e}")
            continue
    return extract_dir


async def extractSubtitles(path_to_file, user_id):
    """
    docs
    """
    dir_name = os.path.dirname(os.path.dirname(path_to_file))
    if not os.path.exists(path_to_file):
        return None
    if not os.path.exists(dir_name + "/extract"):
        os.makedirs(dir_name + "/extract")
    videoStreamsData = ffmpeg.probe(path_to_file)
    # with open("data.json",'w') as f:
    #     f.write(json.dumps(videoStreamsData))
    extract_dir = dir_name + "/extract"
    subtitles = []
    for stream in videoStreamsData.get("streams"):
        try:
            if stream["codec_type"] == "subtitle":
                subtitles.append(stream)
        except Exception as e:
            LOGGER.warning(e)
    for subtitle in subtitles:
        extractcmd = []
        extractcmd.append("ffmpeg")
        extractcmd.append("-hide_banner")
        extractcmd.append("-i")
        extractcmd.append(path_to_file)
        extractcmd.append("-map")
        try:
            index = subtitle["index"]
            extractcmd.append(f"0:{index}")
            try:
                output_file: str = (
                    "("
                    + subtitle["tags"]["language"]
                    + ") "
                    + subtitle["tags"]["title"]
                    + "."
                    + subtitle["codec_type"]
                    + ".srt"
                )
                output_file = output_file.replace(" ", ".")
            except:
                output_file = (
                    str(subtitle["index"]) + "." + subtitle["codec_type"] + ".srt"
                )
            extractcmd.append(f"{extract_dir}/{output_file}")
            LOGGER.info(extractcmd)
            subprocess.call(extractcmd)
        except Exception as e:
            LOGGER.error(f"Unable to extract subtitle {e}")
            continue
    return extract_dir


async def GenerateScreenshot(filePath: str, output_dir: str, ttl: int):
    """
    Generate screenshot from a video file using ffmpeg.
    :param filePath: Path to the video file.
    :param output_dir: Directory to save the screenshot.
    :param ttl: Timestamp to take the screenshot.
    :return: Path to the screenshot.
    """
    output_file_name = os.path.join(output_dir, f"{time.time()}.jpg")
    command = [
        "ffmpeg",
        "-ss",
        str(ttl),
        "-i",
        filePath,
        "-vframes",
        "1",
        output_file_name,
    ]
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    LOGGER.info(e_response)
    LOGGER.info(t_response)
    
    if os.path.lexists(output_file_name):
        return output_file_name
    else:
        return None
