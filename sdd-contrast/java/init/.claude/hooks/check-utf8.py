#!/usr/bin/env python
"""편집된 .java 파일이 유효한 UTF-8인지 검사한다(한글 주석 손상 방지).

PostToolUse(Write|Edit) hook으로 호출된다. stdin으로 받은 JSON에서 파일 경로를
뽑아, .java 파일이면 UTF-8 디코딩과 U+FFFD(깨진 문자) 존재를 확인한다.
문제가 있으면 systemMessage JSON을 출력해 사용자에게 경고한다(차단은 하지 않음).
"""
import sys
import json

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, ValueError):
    sys.exit(0)

path = (data.get("tool_input", {}).get("file_path")
        or data.get("tool_response", {}).get("filePath"))
if not path or not path.endswith(".java"):
    sys.exit(0)

try:
    with open(path, "rb") as fh:
        raw = fh.read()
except OSError:
    sys.exit(0)

try:
    text = raw.decode("utf-8")
except UnicodeDecodeError:
    print(json.dumps({"systemMessage":
        "[encoding] " + path + " 가 유효한 UTF-8이 아닙니다. "
        "한글 주석이 깨질 수 있으니 UTF-8(BOM 없이)로 다시 저장하세요."}))
    sys.exit(0)

if "�" in text:
    print(json.dumps({"systemMessage":
        "[encoding] " + path + " 에 깨진 문자(U+FFFD)가 있습니다 — "
        "인코딩 손상 가능. UTF-8로 다시 저장하세요."}))

sys.exit(0)
