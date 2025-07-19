import logging
import os
import fileinput
import sys
import tempfile



def intercept_port_number_in_js_file(file: str, port_number: int, target_port_number) -> bool:
    if not os.path.exists(file):
        logging.warning("js file not exist!")
        return False
    
    find_port_str = str(port_number)
    target_port_str = str(port_number)

    dirname = os.path.dirname(file) or "."
    tmp_path = os.path.join(dirname, f"{file}-tmp.js")

    overlap = len(find_port_str) - 1
    with open(file, "r", encoding="utf-8") as src, \
         open(tmp_path, "w", encoding="utf-8") as dst:
        buffer = ""
        while True:
            chunk = src.read(1024)
            if len(chunk) == 0:
                dst.write(buffer.replace(find_port_str, target_port_str))
                break

            buffer += chunk
            buffer_len = len(buffer)
            need_replace = True
            if buffer_len >= overlap * 2:
                idx = buffer.find(find_port_str, buffer_len - overlap * 2, buffer_len)
                if idx != -1:
                    buffer = buffer.replace(find_port_str, target_port_str)
                    need_replace = False
                
            write_part = buffer[:-overlap] if overlap > 0 else buffer
            dst.write(
                write_part.replace(find_port_str, target_port_str) if need_replace else write_part
            )
            buffer = buffer[:-overlap] if overlap > 0 else ""
    
    os.rename(file, f"{file}.bak")
    os.rename(tmp_path, file)
    return True

if __name__ == "__main__":
    intercept_port_number_in_js_file(
        file=".\\main.js",
        port_number=64901,
        target_port_number=64900
    )