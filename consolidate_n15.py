from html.parser import HTMLParser
import re

TRACKED_TAGS = ("body", "span", "p", "ol", "ul", "li", "h1", "h2", "h3", "h4", "a")

class N15Consolidator(HTMLParser):
    def __init__(self):
      super().__init__()
      self.stack : list[tuple[str, list[str]]] = []
      self.committed_stack : list[tuple[int, tuple[str, list[str]]]] = []
      self.out = ""

    def current_classes(self):
      return set(c for _, classes in self.stack for c in classes)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str|None]]):
      if tag in TRACKED_TAGS:
        attrs : dict[str, str|None] = dict(attrs)
        classes = (attrs.get("class") or "").split(" ")
        self.stack.append((tag, classes))

    def handle_endtag(self, tag: str):
      if tag in TRACKED_TAGS:
        top = self.stack.pop()
        if len(self.stack) == self.committed_stack[-1][0]:
          self.out += f"</{output_tag(top)}\n>"
          self.committed_stack.pop()
        if top[0] != tag:
          print(top, "closed by", tag)

    def handle_data(self, data: str):
      if not self.stack:
        return
      # c1: struck through; c7, c39: drafter’s notes.
      IGNORABLE_CLASSES = ["c1", "c7", "c39"]
      if all(c not in IGNORABLE_CLASSES for c in self.current_classes()):
        header = any(re.match(r"h\d", tag) for tag, _classes in self.stack)
        for i in range(self.committed_stack[-1][0] + 1 if self.committed_stack
                           else 0,
                       len(self.stack)):
          candidate = self.stack[i]
          if header and candidate[0] in ("ol", "li"):
            continue
          if output_tag(candidate) == "span":
            continue
          self.out += f"<{output_tag(candidate)}\n>"
          self.committed_stack.append((i, candidate))
        self.out += data

def output_tag(stack_element : tuple[str, list[str]]):
  tag, classes = stack_element
  if tag == "span" and "c13" in classes:
    return "i"
  return tag

consolidator = N15Consolidator()
with open("DRAFT10646MAbicameralToR.docx.html", encoding="utf8") as f:
  consolidator.feed(f.read())
with open("N15.html", "w", encoding="utf8") as out:
  out.write("<meta charset=utf-8>\n")
  out.write(consolidator.out)