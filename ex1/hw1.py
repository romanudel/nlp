import sys
import re
import bs4


def to_plain_text(input_html, path_to_output_files):
    tag_names = ['p', 'h1', 'h2', 'h3', 'ul']
    to_file_str = ''

    file_input = open(input_html, "r", encoding='utf8')
    file_output = open(path_to_output_files, "w+", encoding='utf8')

    soup = bs4.BeautifulSoup(file_input, 'html.parser')
    # Start point for html parsing is the arcicale tag.
    tag_article = soup.article

    for sib in tag_article.descendants:
        if sib.name == 'h1':
            # file_output.write(sib.text+"\t")
            to_file_str = to_file_str + sib.text.rstrip() + "\r"
        if sib.name == 'section':
            for tag_name in tag_names:

                for sib_tag in sib.find_all(tag_name, {"class": False}):
                    ####
                    if sib_tag == 'h3' and sib_tag.children == 'p':
                        to_file_str = to_file_str + sib_tag.text.rstrip() + ' '
                        ####
                    if sib_tag.parent.name == 'section' and (sib_tag.parent.attrs.get('class')[0] == 'post-content'):
                        to_file_str = to_file_str + sib_tag.text.rstrip() + '\r'
                        # print(sib_tag.name + " " + sib_tag.parent.name )
    file_output.write(to_file_str)
    file_input.close()
    file_output.close()
    return path_to_output_files


def to_lines_list(plain_text, path_to_output_files):
    lines_list = []
    # regular expretion for separators.
    separators_pattern = '((?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|;|!|\?)\s)'
    lines_list = []
    file_output = open(path_to_output_files, "w+", encoding='utf8')

    for line in open(plain_text, 'r', encoding='utf8'):

        # splits the line sperated with delimiter from the pattern.each sentence and its delimiter in diffrent cell.
        splited_list = re.split(separators_pattern, line)

        ##sentences located at even places - while the delimiters in odd places .It will rejoin the delimiter to the sentence.
        # before that check if the lenght of splited_list is even or odd - if odd then make it even by insert '' element to the list
        if len(splited_list) % 2 == 1:
            splited_list.insert(-1, '')
        joined_list = [x + y for x, y in zip(splited_list[0::2], splited_list[1::2])]

        # if list is not empty
        if joined_list:
            for a in joined_list:
                ## Remove empty lines if exists
                #  Line consider to be empty  if it has: '\t','\n','\r' or '' )
                if re.match(r'^\s*$', a) or re.match(r'^$', a):
                    continue
                lines_list.insert(-1, a.rstrip())
                file_output.write(a.rstrip() + '\n')
    file_output.close()
    return lines_list


def clean_hidden_chars(path_to_output_files):
    new_string = ''

    for line in open(path_to_output_files, 'r', encoding='utf8'):

        # if the line is empty
        if re.match(r'^\s$', line):
            continue
        # remove hidden charachters from the end of the line
        line = re.split(r'[\s]+$', line)[0]

        new_string = new_string + line + ' '

    file_output = open(path_to_output_files, "w+", encoding='utf8')
    file_output.write(new_string)
    file_output.close()

REGEX = r'(' \
        r'(?# numeric date handling)('+\
        r''.join(['(?:[\d]{0}1,2{1}{2}[\d]{0}1,2{1}{2}(?:[\d]{0}4{1}|[\d]{0}2{1}))|'
                  '(?:(?:[\d]{0}4{1}|[\d]{0}2{1}){2}[\d]{0}1,2{1}{2}[\d]{0}1,2{1})|'.format('{', '}', x)
                  for x in ["/", "\.", "-"]])[:-1] + r')|' \
        r'(?# israeli style domestic phone numbers)(?:(?:(?:\+972-\d{4}1,2{5})|\d{4}2,3{5})-[\d]{4}7{5})|'\
        r'(?# comma separated numbers:)' \
        r'(?:\d{4}1,3{5}(?:,\d{4}3{5})+\.[\d]+)|(?:\d{4}1,3{5}(?:,\d{4}3{5})+)|(?:\d{4}1,3{5}\.[\d]+)|' \
        r'(?# Time formats hour:min[:sec][AM|PM] where all digits may be single or double:)' \
        r'(?:[\d]{4}1,2{5}(?::[\d]{4}1,2{5}){4}1,2{5}(?:am|pm|AM|PM)?)|' \
        r'(?# Apostrophe as abreaviation or scpecial hebrew sound:)(?:(?:[{2}]+[{3}])+[{2}]*)|' \
        r'(?# Hebrew abreviations using quotations marks before the last letter:)(?:[{1}]+?[{6}][{1}])(?=[^{2}]+)|' \
        r'(?:\w+[\@\#\*]+)|' \
        r'[{0}]|' \
        r'[\w]+' \
        r')'.format(
            r"^\w ",
            "א-ת",
            r"a-zA-Zא-ת",
            r"\׳\'",
            "{",
            "}",
            "\״\"")

def to_tokens(lines_list, path_to_output_files):
    def f(p):
        if type(p) is str:
            return p
        for x in p:
            if x != '':
                return x+" "
        return " "
    with open(path_to_output_files, "w+", encoding='utf8') as o:
        for line in lines_list:
            tokens = list(map(f, re.findall(REGEX, line, re.UNICODE))) + ['\n']
            print(tokens)
            o.writelines(tokens)

def main():
    if len(sys.argv) != 3:
        print("missing/too many arguments!")
        return 2

    input_html = sys.argv[1]
    path_to_output_files = sys.argv[2]

    to_plain_text(input_html, path_to_output_files+"/article.txt")
    lines_list = to_lines_list(path_to_output_files+"/article.txt", path_to_output_files+"/article_sentences.txt")
    clean_hidden_chars(path_to_output_files+"/article.txt")
    to_tokens(lines_list, path_to_output_files+"/article_tokenized.txt")
if __name__ == "__main__":
    sys.exit(main())