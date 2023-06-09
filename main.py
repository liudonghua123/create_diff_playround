from flet import *
from flet_core.file_picker import FilePickerFile
from enum import Enum
from difflib import unified_diff, context_diff
from typing import Self

class File_MODE(Enum):
  FILE1 = 1
  FILE2 = 2

  @staticmethod
  def parse_from(value: str | Self) -> Self:
    if type(value) == File_MODE:
      return value
    if value == "File_MODE.FILE1":
      return File_MODE.FILE1
    elif value == "File_MODE.FILE2":
      return File_MODE.FILE2

class DIFF_MODE(Enum):
  UNIFIED = 1
  CONTEXT = 2

  @staticmethod
  def parse_from(value: str | Self) -> Self:
    if type(value) == DIFF_MODE:
      return value
    if value == "DIFF_MODE.UNIFIED":
      return DIFF_MODE.UNIFIED
    elif value == "DIFF_MODE.CONTEXT":
      return DIFF_MODE.CONTEXT


current_file_mode = File_MODE.FILE1
current_diff_mode = DIFF_MODE.UNIFIED
txt_content1 = TextField(label="content 1", multiline=True, min_lines=10, height=200)
txt_content2 = TextField(label="content 2", multiline=True, min_lines=10, height=200)
txt_diff = TextField(label="diff", multiline=True, min_lines=10, height=200)

def diff_mode_handler(e: ControlEvent):
  global current_diff_mode
  current_diff_mode = DIFF_MODE.parse_from(e.control.value)


cg = RadioGroup(
    content=Column([
        Radio(value=DIFF_MODE.UNIFIED, label="unified"),
        Radio(value=DIFF_MODE.CONTEXT, label="context"),
    ]),
    on_change=diff_mode_handler,
    value=current_diff_mode,
)

def split_lines_keep_delimiter(text: str) -> list[str]:
  # https://bobbyhadz.com/blog/python-split-string-without-removing-delimiter
  # return [f"{line}\n" for line in text.split("\n")]
  # >>> s='bacon\neggs\n\nham\nguido\n'
  # >>> s.splitlines(keepends=True)
  # ['bacon\n', 'eggs\n', '\n', 'ham\n', 'guido\n']
  # >>> split_lines_keep_delimiter(s)
  # ['bacon\n', 'eggs\n', '\n', 'ham\n', 'guido\n', '\n']
  # >>> s.split("\n")
  # ['bacon', 'eggs', '', 'ham', 'guido', '']
  # >>> s='bacon\neggs\n\nham\nguido'
  # >>> s.splitlines(keepends=True)
  # ['bacon\n', 'eggs\n', '\n', 'ham\n', 'guido']
  # >>> split_lines_keep_delimiter(s)
  # ['bacon\n', 'eggs\n', '\n', 'ham\n', 'guido\n']
  # >>>
  # splited_text = text.split("\n")
  # results = []
  # for index, item in enumerate(splited_text):
  #   if index < len(splited_text) - 1:
  #     results.append(f"{item}\n")
  #   else:
  #     results.append(item)
  # return results
  # Every parts of the splitted text should be ended with \n, or the diff will not work correctly
  # Method 1:
  # [f"{line}\n" for line in "".join(['bacon\n', 'eggs\n', 'ham\n', 'guido']).split('\n')] => ['bacon\n', 'eggs\n', 'ham\n', 'guido\n']
  # [f"{line}\n" for line in "".join(['bacon\n', 'eggs\n', 'ham\n', 'guido\n']).split('\n')] => ['bacon\n', 'eggs\n', 'ham\n', 'guido\n', '\n']
  # return [f"{line}\n" for line in text.split("\n")]
  # Method 2:
  # "".join(['bacon\n', 'eggs\n', 'ham\n', 'guido']).splitlines(keepends=True) => ['bacon\n', 'eggs\n', 'ham\n', 'guido'] # the last item is not ended with \n
  # "".join(['bacon\n', 'eggs\n', 'ham\n', 'guido\n']).splitlines(keepends=True) => ['bacon\n', 'eggs\n', 'ham\n', 'guido\n']
  if not text.endswith("\n"):
    text += "\n"
  return text.splitlines(keepends=True)

def init_layout(page: Page):

  def picker_file_1_handler(e: ControlEvent):
    global current_file_mode
    current_file_mode = File_MODE.FILE1
    file_picker.pick_files()

  def picker_file_2_handler(e: ControlEvent):
    global current_file_mode
    current_file_mode = File_MODE.FILE2
    file_picker.pick_files()

  def read_file_content(file_picker_file: FilePickerFile):
    # https://flet.dev/docs/controls/filepicker#result
    # path - full path to a file. Works for desktop and mobile only. None on web.
    # TODO: support web, add bytes property to FilePickerFile
    # see also https://github.com/miguelpruivo/flutter_file_picker#load-result-and-file-details
    if file_picker_file.bytes:
      return bytes.decode(file_picker_file.bytes)
    if file_picker_file.path:
      with open(file_picker_file.path, "r") as f:
        return f.read()

  def on_file_pick_result(e: FilePickerResultEvent):
    global current_file_mode
    choosed_file: FilePickerFile = e.files[0] if e.files else None
    txt_content = txt_content1 if current_file_mode == File_MODE.FILE1 else txt_content2
    if choosed_file:
      txt_content.value = read_file_content(choosed_file)
    page.update()

  def create_diff_handler(e: ControlEvent):
    global current_diff_mode
    if current_diff_mode == DIFF_MODE.UNIFIED:
      txt_diff.value = "".join(unified_diff(split_lines_keep_delimiter(txt_content1.value), split_lines_keep_delimiter(txt_content2.value)))
    elif current_diff_mode == DIFF_MODE.CONTEXT:
      txt_diff.value = "".join(context_diff(split_lines_keep_delimiter(txt_content1.value), split_lines_keep_delimiter(txt_content2.value)))
    page.update()

  file_picker = FilePicker(on_result=on_file_pick_result)
  page.overlay.append(file_picker)

  common_padding = 10
  page.add(
      ResponsiveRow(
          [
              Card(
                  col=6,
                  color=colors.ORANGE_50,
                  content=Container(
                      content=Column(
                          controls=[
                              OutlinedButton(
                                  icon="file", text="Choose file 1", on_click=picker_file_1_handler
                              ),
                              txt_content1,
                          ]
                      ),
                      padding=common_padding,
                  ),
              ),
              Card(
                  col=6,
                  color=colors.YELLOW_50,
                  content=Container(
                      content=Column(
                          controls=[
                              OutlinedButton(
                                  icon="file", text="Choose file 2", on_click=picker_file_2_handler
                              ),
                              txt_content2,
                          ]
                      ),
                      padding=common_padding,
                  ),
              ),
          ]
      ),
      Card(
          Container(
              content=Row(
                  [Text("diff mode: "), cg, FilledButton("Create diff", on_click=create_diff_handler, expand=True)]
              ),
              padding=common_padding,
          ),
      ),
      ResponsiveRow(
          [
              Container(
                  content=Card(
                      color=colors.BLUE_50,
                      content=txt_diff,
                  ),
                  padding=common_padding,
              ),
          ]
      )
  )


def main(page: Page):
  page.title = "Create diff playround"
  init_layout(page)


app(target=main)
