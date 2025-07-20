import asyncio
from dataclasses import dataclass
from datetime import datetime
import filecmp
import logging
import os
from typing import Optional
import aiofiles
from lxml import html


async def update_main_js_port_number(
    main_js_path: str, port_number: int, target_port_number: int
) -> bool:
    print("find port: {}, update to {}".format(port_number, target_port_number))
    main_js_path = os.path.abspath(main_js_path)
    if not os.path.exists(main_js_path):
        return False

    find_port_str = str(port_number)
    target_port_str = str(target_port_number)
    
    dirname = os.path.dirname(main_js_path) or "."
    tmp_path = os.path.join(dirname, f"{main_js_path}-tmp.js.bak")
    
    overlap = len(find_port_str)
    try:
        async with aiofiles.open(main_js_path, "r", encoding="utf-8") as src:
            async with aiofiles.open(tmp_path, "w", encoding="utf-8") as dst:
                buffer = ""
                buffer_size = 4 * 1024
                while True:
                    chunk = await src.read(buffer_size)
                    if chunk is None or len(chunk) == 0:
                        await dst.write(buffer.replace(find_port_str, target_port_str))
                        break
                    buffer += chunk
                    await dst.write(
                        buffer.replace(find_port_str, target_port_str)
                    )
                    len_buffer = len(buffer)        
                    buffer = buffer[len_buffer - overlap:len_buffer] if len_buffer > overlap else buffer
                        
        backup_file =  f"{main_js_path}-{int(datetime.now().timestamp())}.bak"
        os.rename(main_js_path, backup_file)
        os.rename(tmp_path, main_js_path)
        return True
    except:
        logging.exception("error update")
        return False


@dataclass
class PTATFiles:
    ptat_path: str
    launcher_path: str
    main_js_path: str


def locate_ptat_files_ex(ptat_path: str) -> PTATFiles:
    files = PTATFiles("", "", "")
    files.ptat_path = ptat_path
    if not os.path.exists(ptat_path):
        raise FileNotFoundError("{} 不存在！".format(ptat_path))

    files.launcher_path = os.path.join(ptat_path, "PTATLauncher.exe")
    if not os.path.exists(files.launcher_path):
        raise FileNotFoundError("PTATLauncher.exe 不存在！")

    ptat_ui_path = os.path.join(
        ptat_path,
        "UI",
    )
    ptat_index_html_path = os.path.join(ptat_ui_path, "index.html")
    if not os.path.exists(ptat_index_html_path):
        raise FileNotFoundError("UI/index.html 不存在！")

    ptat_main_js_path = ""
    with open(ptat_index_html_path, "r", encoding="utf-8") as f:
        try:
            root = html.fromstring(f.read())
            elements = root.findall("body/script")
            for elem in elements:
                script_name: str = elem.attrib["src"]
                if script_name.startswith("main.aac") and script_name.endswith("js"):
                    ptat_main_js_path = os.path.join(ptat_ui_path, script_name)
                    break
        except Exception as e:
            raise RuntimeError("index.html 文件解析异常！{}".format(e))
    if len(ptat_main_js_path) <= 0:
        raise FileNotFoundError(
            "index.html 异常，请检查 script 标签是否存在 main 前缀文件！"
        )
    if not os.path.exists(ptat_main_js_path):
        raise FileNotFoundError("{} 文件不存在！".format(ptat_main_js_path))

    files.main_js_path = ptat_main_js_path
    return files


def __parse_number(buffer: str, target_str: str, results: list[int]):
    buffer_len = len(buffer)
    if buffer_len <= 0:
        return
    start_idx = 0
    len_target_str = len(target_str)
    while (find_idx := buffer.find(target_str, start_idx, buffer_len)) != -1:
        find_idx = idx = find_idx + len_target_str
        while idx < buffer_len and buffer[idx].isnumeric():
            idx += 1
        num_str = buffer[find_idx:idx]
        if num_str.isnumeric():
            results.append(int(num_str))
        start_idx = idx


async def extract_ptat_main_js_port(main_js_path: str) -> Optional[int]:
    """
    提取出 main.aac----.js 文件中声明的端口号.
    """
    if not os.path.exists(main_js_path):
        logging.error("{} 文件不存在".format(main_js_path))
        return None
    target_str = "this.portNumber="
    overlap_len = len(target_str) + 10 # 端口号最多应该只有5位
    find_port_number: Optional[int] = 0
    results: list[int] = []
    async with aiofiles.open(main_js_path, "r", encoding="utf-8") as f:
        # TODO: 文件操作应该是可以共享一个缓存区的
        pre_buffer = ""
        buffer = ""
        buffer_size = 4 * 1024
        while True:
            content = await f.read(buffer_size)
            if content is None or len(content) == 0:
                __parse_number(buffer, target_str, results)
                break
            pre_buffer = buffer[:overlap_len] if len(buffer) >= overlap_len else buffer
            buffer = content
            if len(pre_buffer) + len(buffer) <= buffer_size:
                continue
            __parse_number(pre_buffer + buffer, target_str, results)

    if len(results) > 0:
        find_port_number = results[0]
        for item in results:
            assert item == find_port_number
    return find_port_number


if __name__ == "__main__":
    result = asyncio.run(
        update_main_js_port_number(
            "utils/main.js",
            port_number=64901,
            target_port_number=64900,
        )
    )
    print(result)
