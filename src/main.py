import markdown
from markdown import Extension
from markdown.postprocessors import Postprocessor
from imgur import upload_to_imgur
import util
import io
import os
import re


images = []

RE_SLASH_WIN_DRIVE = re.compile(r"^/[A-Za-z]{1}:/.*")

file_types = {
    (".png",): "image/png",
    (".jpg", ".jpeg"): "image/jpeg",
    (".gif",): "image/gif",
    (".svg",): "image/svg+xml",
    (".webp",): "image/webp",
}

RE_TAG_HTML = re.compile(
    r'''(?xus)
    (?:
        (?P<avoid>
            <\s*(?P<script_name>script|style)[^>]*>.*?</\s*(?P=script_name)\s*> |
            (?:(\r?\n?\s*)<!--[\s\S]*?-->(\s*)(?=\r?\n)|<!--[\s\S]*?-->)
        )|
        (?P<open><\s*(?P<tag>img))
        (?P<attr>(?:\s+[\w\-:]+(?:\s*=\s*(?:"[^"]*"|'[^']*'))?)*)
        (?P<close>\s*(?:\/?)>)
    )
    '''
)

RE_TAG_LINK_ATTR = re.compile(
    r'''(?xus)
    (?P<attr>
        (?:
            (?P<name>\s+src\s*=\s*)
            (?P<path>"[^"]*"|'[^']*')
        )
    )
    '''
)


def repl_path(m, base_path):
    """Replace path with Imgur link."""

    link = m.group(0)

    try:
        path, is_url, is_absolute = util.parse_url(
            m.group('path')[1:-1])

        if not is_url:
            path = util.url2path(path)

            if is_absolute:
                file_name = os.path.normpath(path)
            else:
                file_name = os.path.normpath(os.path.join(base_path, path))

            if os.path.exists(file_name):
                link = upload_to_imgur(path)
                images.append({'path': path, 'link': link})
    except Exception:
        pass

    return link


def repl(m, base_path):
    """Replace."""

    if m.group('avoid'):
        tag = m.group('avoid')
    else:
        tag = m.group('open')
        tag += RE_TAG_LINK_ATTR.sub(lambda m2: repl_path(m2,
                                    base_path), m.group('attr'))
        tag += m.group('close')
    return tag


class ImgurPostprocessor(Postprocessor):
    def run(self, text):
        """Find and replace paths with base64 encoded file."""

        basepath = self.config['base_path']
        text = RE_TAG_HTML.sub(lambda m: repl(m, basepath), text)
        return text


class ImgurExtension(Extension):
    def __init__(self, *args, **kwargs):
        self.config = {
            'base_path': [".", "Base path for ImgurPostprocessor to use to resolve paths"]
        }
        super(ImgurExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md):
        """Add base 64 tree processor to Markdown instance."""

        imgur_post_processor = ImgurPostprocessor(md)
        imgur_post_processor.config = self.getConfigs()
        md.postprocessors.register(
            imgur_post_processor, "imgur_post_processor", 2)
        md.registerExtension(self)


data = io.open('original.md', 'r', encoding='UTF-8').read()

md = markdown.markdown(data, extensions=[ImgurExtension()])

for image in images:
    data = data.replace(image['path'], image['link'])

updated = io.open('updated.md', 'w+', encoding='UTF-8')
updated.write(data)
updated.close()
