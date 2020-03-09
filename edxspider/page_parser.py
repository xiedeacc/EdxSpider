import html
import json
import typing
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse

def parse_page(index_doc: str, item_list_file: typing.TextIO = None) -> list:
    all_content = []
    document = BeautifulSoup(index_doc, 'lxml')
    seq_list_ol = document.find(id = "sequence-list")
    all_seq_content_li = seq_list_ol.find_all("li")
    for seq_content_li in all_seq_content_li:
        # Construct a 'content' object to gather information
        content = dict()
        data_index = seq_content_li.button["data-index"]
        data_path = seq_content_li.button["data-path"]
        content["title"] = data_path
        content["index"] = data_index
        # Parse inner html then find out video and transcript links
        seq_content = document.find(id = "seq_contents_%s" % data_index)
        inner_html = seq_content.get_text()
        inner_document = BeautifulSoup(inner_html, 'html.parser')
        video_link_el = inner_document.find(class_ = "btn-link video-sources video-download-button")
        content["video_link"] = video_link_el["href"] if video_link_el else None
        transcript_link_el = inner_document.find(class_ = "btn-link external-track")
        content["transcript_link"] = transcript_link_el["href"] if transcript_link_el else None
        if content["transcript_link"]:
            u = urlparse(content["transcript_link"])
            if not u.scheme:
                u = u._replace(scheme='https')
            if not u.netloc:
                u = u._replace(netloc='courses.edx.org')
            content["transcript_link"] = urlunparse(u)
        # Extract exercise content
        if not video_link_el:
            inner_html_esc = html.unescape(inner_html)
            inner_document = BeautifulSoup(inner_html_esc, 'html.parser')
            problem_el = inner_document.find(class_ = "problem")
            if problem_el:
                content["html_text"] = str(problem_el.div)
        all_content.append(content)
    # Write item list
    if item_list_file:
        json.dump(all_content, item_list_file)

    return all_content

    